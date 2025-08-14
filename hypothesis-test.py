import pandas as pd
# from numpy.random import seed
# from numpy.random import randn
from scipy.stats import mannwhitneyu
from scipy.stats import kruskal
from scipy.stats import chi2_contingency
from util import glob_get_files_list,read_csv
# seed the random number generator
# seed(1)
# generate two independent samples
# data1 = 5 * randn(1000) + 50
# data2 = 5 * randn(100) + 50
#data1 = [19, 22, 16, 29, 24]
#data2 = [20, 11, 17, 12]
#data1 = [48, 40, 39, 50, 41, 38, 53]
#data2 = [14, 18, 20, 10, 12, 102, 17]

# File paths
output_folder = "./pcap/output/"
working_folder = output_folder + "4-ML/"
# models_folder = working_folder + "models/" # read the models from here
input_files_path_preprocessed_data = working_folder + "preprocess/data_ready_to_ml/" # read preprocessed data from here

def chi_squared_hypothesis_test(data1, data2):
    # Pearson's chi-squared test
    # For more information, see
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.contingency.chi2_contingency.html

    counts1 = data1.value_counts().sort_index()
    counts2 = data2.value_counts().sort_index()
    table = [counts1.reindex(counts2.index, fill_value=0).tolist(), counts2.tolist()]
    
    print("[DEBU] === Chi-Squared Test ===")
    stat, p, dof, expected = chi2_contingency(table)
    alpha = 0.05 # 95% confidence level
    passed = p > alpha
    print('[DEBU] stat=%.3f, p=%.3f' % (stat, p))
    if passed:
        print('[DEBU] Probably independent (fail to reject H0)')
    else:
        print('[DEBU] Probably dependent (reject H0)')
    return alpha, stat, p, passed

def kruskal_wallis_hypothesis_test(data1, data2):
    # Kruskal-Wallis H-test
    # For more information, see
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.kruskal.html
    # and Chapter 6 (page 117) in
    # G. W. Corder and D. I. Foreman, Nonparametric statistics: a step-by-step approach. 
    # Hoboken (N.J.): Wiley, Cop, 2014

    try:
        stat, p = kruskal(data1, data2)
        alpha = 0.05 # 95% confidence level
        passed = p <= alpha
        print("[DEBU] === Kruskal-Wallis H-test ===")
        print('[DEBU] Statistics=%.3f, p=%.3f' % (stat, p))
        if passed:
            print('[DEBU] Different distributions (reject H0)')
        else:
            print('[DEBU] Same distributions (fail to reject H0)')
        return alpha, stat, p, passed
    except ValueError as e:
        print(f"[INFO] Skipping Kruskal Wallis H Test due to {e}")
        return None, None, None, None
        

def mann_whitney_hypothesis_test(data1, data2):
    # Mann-Whitney U test
    # For details on the parameters below, see
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.mannwhitneyu.html
    # and page 75 in
    # G. W. Corder and D. I. Foreman, Nonparametric statistics: a step-by-step approach. 
    # Hoboken (N.J.): Wiley, Cop, 2014
    # NOTE Not using it for now because Kruskal Wallis is more general
    # https://en.wikipedia.org/wiki/Kruskal%E2%80%93Wallis_test

    n1 = len(data1)
    n2 = len(data2)
    # compare samples
    u1, p = mannwhitneyu(data1, data2)
    u2 = n1 * n2 - u1
    stat = min(u1, u2)
    print("[DEBU] === Mann-Whitney U Test ===")
    print('[DEBU] Statistics1 (U1) = %.3f\n Statistics2 (U2) = %.3f\n p = %.3f' % (u1, u2, p))

    # statistical results
    print("[DEBU] U:", stat)
    print("[DEBU] n1:", n1)
    print("[DEBU] n2:", n2)

    # interpret
    alpha = 0.05 # 95% confidence level
    passed = p > alpha
    if passed:
        print("[DEBU] p > alpha")
        print("[DEBU] %.3f > %.2f" % (p, alpha))
        print('[DEBU] Same distribution (fail to reject H0)')
    else:
        print("[DEBU] p < alpha")
        print("[DEBU] %.3f < %.2f" % (p, alpha))
        print('[DEBU] Different distribution (reject H0)')

    return alpha, stat, p, passed

def load_data(csv_files_list):
    data = {
        'training_embb': pd.DataFrame(),
        'training_urllc': pd.DataFrame(),
        'training_mmtc': pd.DataFrame(),
        'inference_embb': pd.DataFrame(),
        'inference_urllc': pd.DataFrame(),
        'inference_mmtc_burst': pd.DataFrame(),
        'inference_mmtc_prob': pd.DataFrame(),
    }

    print("[INFO] Loading files ... ", end='', flush=True)
    for file in csv_files_list:
        if 'training' in file and 'embb' in file:
            data['training_embb'] = pd.read_csv(file)
        elif 'training' in file and 'urllc' in file:
            data['training_urllc'] = pd.read_csv(file)
        elif 'training' in file and 'mmtc' in file:
            df = pd.read_csv(file)
            data['training_mmtc'] = pd.concat([data['training_mmtc'], df], ignore_index=True)
        elif 'inference' in file and 'embb' in file:
            data['inference_embb'] = pd.read_csv(file)
        elif 'inference' in file and 'urllc' in file:
            data['inference_urllc'] = pd.read_csv(file)
        elif 'inference' in file and 'mmtc' in file and '100pps' in file:
            data['inference_mmtc_burst'] = pd.read_csv(file)
        elif 'inference' in file and 'mmtc' in file and '1k' in file:
            data['inference_mmtc_prob'] = pd.read_csv(file)
        else:
            raise ValueError(f"[ERRO] Could not determine dataset type from filename {file}")
    print("[ OK ]")

    return data

# Buid the CSV files list
csv_files = glob_get_files_list(input_files_path_preprocessed_data, file_format="csv")

# Load the data
data = load_data(csv_files)

# Access the dataset DataFrames using the keys
training_embb_data = data['training_embb']
training_urllc_data = data['training_urllc']
training_mmtc_data = data['training_mmtc']
inference_embb_data = data['inference_embb']
inference_urllc_data = data['inference_urllc']
inference_mmtc_burst_data = data['inference_mmtc_burst']
inference_mmtc_prob_data = data['inference_mmtc_prob']

# Define a list of feature names to test
feature_names = ["Time_delta", "Timestamp", "TCP_window_size", "Frame_total_length", "QUIC_packet_length", "TCP_completeness", 
                 "TCP_header_length", "Frame_payload_length", "TCP_window_size_scale"]

# Define a list of dataset pairs to test
data_to_be_tested = [
    (training_embb_data, inference_embb_data, "eMBB"),
    (training_urllc_data, inference_urllc_data, "URLLC"),
    (training_mmtc_data, inference_mmtc_burst_data, "mMTC (burst)"),
    (training_mmtc_data, inference_mmtc_prob_data, "mMTC (prob.)"),
]

# Initialize a list to store results
results = []

# Loop through the datasets and feature names to run the tests
for train_data, infer_data, class_label in data_to_be_tested:
    print(f"[INFO] Testing class {class_label}", flush=True)
    for feature in feature_names:
        df1 = train_data[feature]
        df2 = infer_data[feature]

        print(f"[INFO] Testing {feature} feature", flush=True)

        if feature == "Time_delta" or feature == "Timestamp":
            test_name = "Mann-Whitney U test"
            alpha, stat, p, passed = mann_whitney_hypothesis_test(df1, df2)
        else:
            test_name = "Chi-Squared Test"
            alpha, stat, p, passed = chi_squared_hypothesis_test(df1, df2)

        # Store the results
        if alpha is not None and p is not None:
            results.append({
                'label': class_label,
                'feature': feature,
                'test_name': test_name,
                'stat': stat,
                'alpha': alpha,
                'p': p,
                'pass': passed
            })

# Convert results to a DataFrame and save to CSV
results_df = pd.DataFrame(results)
results_file_name = "hypothesis_test_results.csv"
results_file_path = output_folder + results_file_name
results_df.to_csv(results_file_path, index=False)
print(f"[INFO] Results saved to {results_file_path}")
