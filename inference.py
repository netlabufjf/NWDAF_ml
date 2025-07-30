import pandas as pd
import numpy as np
import pickle
from datetime import datetime
from time import time_ns
from sklearn.metrics import (accuracy_score,
                            precision_score,
                            recall_score,
                            f1_score,
                            roc_auc_score,
                            confusion_matrix)

from util import glob_get_files_list,read_csv,label_id_to_text,plot_confusion_matrix,read_and_label_data,preprocess_data

# File paths
working_folder = "./pcap/output/4-ML/"
input_files_path = working_folder + "preprocess/labeled_files/" # read labeled data CSV files from here
output_files_path_preprocessed_data = working_folder + "preprocess/data_ready_to_ml/" # save preprocessed data there
models_folder = working_folder + "models/" # read the models from here
data_folder = working_folder + "preprocess/labeled_data/" # save or read the inference data from here
results_folder = working_folder + "inference_results/" # save the results here

timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")

def run_inference(models_file_list, inference_data_file_list):
    for file in inference_data_file_list:
        file_name = file.split('/')[-1]

        if 'inference' in file:
            print("[INFO] Running inference on", file_name)
            
            columns = ["file_name", "file_num_rows", "model_name",
                        "inference_result_label", "inference_result",
                        "accuracy", "precision", "recall", "f_score_class",
                        "inference_result_count_0", "inference_result_count_1", "inference_result_count_2",
                        "inf_disk_time_ms", "inf_pred_time_ms", "inf_total_time_ms"]
            # Initialize results_df with columns
            results_df = pd.DataFrame(columns=columns)
            
            data = read_csv(file) # load inference data
            data_num_rows = len(data)

            for path in models_file_list:
                total_inference_time_begin = time_ns()
                model_load_time_begin = time_ns()
                model = pickle.load(open(path, 'rb')) # load model from disk
                model_load_time_end = time_ns() # TODO measure and save it
                model_name = model.__class__.__name__ 
                print("[INFO] Using", model_name)
                
                y_true = data['label'] # save the labels for evaluation
                true_label = y_true.iloc[0] # save true label sample for evaluation
                inference_data = data.drop('label', axis=1)  # remove the label column
                
                inference_pred_time_begin = time_ns()
                y_pred = model.predict(inference_data)
                inference_pred_time_end = time_ns()
                inference_result = pd.Series([model.classes_[i] for i in y_pred])
                inference_result_counts = inference_result.value_counts()
                inference_result_int = inference_result_counts.idxmax()
                inference_result_label = label_id_to_text(inference_result_int)
                total_inference_time_end = time_ns()
                # print(f"[DEBU] Inference result: {inference_result_int} ({inference_result_label})")  # DEBUG
                # print(f"[DEBU] Labels and their occurrences:\n{inference_result_counts}")  # DEBUG

                total_inference_time = (total_inference_time_end - total_inference_time_begin) / 10**6
                inference_pred_time = (inference_pred_time_end - inference_pred_time_begin) / 10**6
                inference_disk_time = (model_load_time_end - model_load_time_begin) / 10**6

                # Model evaluation data
                accuracy = accuracy_score(y_true, y_pred)
                cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])
                precision = precision_score(y_true, y_pred, average="weighted", zero_division=np.nan, labels=[true_label])
                recall = recall_score(y_true, y_pred, average="weighted", zero_division=np.nan)
                f_score_class = f1_score(y_true, y_pred, average="weighted", zero_division=np.nan, labels=[true_label])
                plot_confusion_matrix(cm, results_folder, file_name, model_name, "inference", timestamp, True, False)

                # print("[DEBU] Accuracy:", round(accuracy, 10))
                # print(f"[DEBU] Confusion Matrix:\n{cm}")
                # print("[DEBU] Precision :", round(precision, 10))
                # print("[DEBU] Recall    :", round(recall, 10))
                # print("[DEBU] F1-score of class :", round(f_score_class, 10))
                # if (model_name != "LinearSVC"): # LinearSVC doesn't implement proba
                #     auc_score = roc_auc_score(y_true, model.predict_proba(inference_data), average='macro', multi_class='ovo', labels=[0, 1, 2])
                #     print("[DEBU] ROC AUC Score :", round(auc_score, 10))
                # else:
                #     print("[DEBU] ROC AUC Score : Not calculated for", model_name)
                #     auc_score = "N.A."
                # TODO fix ROC AUC score
                # RuntimeWarning: invalid value encountered in scalar divide ret = ret.dtype.type(ret / rcount) /n [DEBU] ROC AUC Score : nan
                                
                new_row = {
                    columns[0]: file_name,
                    columns[1]: data_num_rows,
                    columns[2]: model_name,
                    columns[3]: inference_result_label,
                    columns[4]: inference_result_int,
                    columns[5]: accuracy,
                    columns[6]: precision,
                    columns[7]: recall,
                    columns[8]: f_score_class,
                    columns[9]: int(inference_result_counts[0]) if 0 in inference_result_counts else 0,
                    columns[10]: int(inference_result_counts[1]) if 1 in inference_result_counts else 0,
                    columns[11]: int(inference_result_counts[2]) if 2 in inference_result_counts else 0,
                    columns[12]: inference_disk_time,
                    columns[13]: inference_pred_time,
                    columns[14]: total_inference_time,
                }
                
                # Add new row to the dataframe using loc[] method
                results_df.loc[len(results_df)] = new_row
                
            # Get the original input file name without format
            output_filename = file_name.split('/')[-1].split('_inference_')[0]
            # Save the results dataframe to a CSV file with a unique filename based on the current time
            results_df.to_csv(f"{results_folder}{output_filename}_{timestamp}_inference_results.csv", index=False)

        else:
            print(f"[WARN] Skipping file {file_name}")

print("[INFO] Running inference preprocess")
# Run preprocess in case the inference data wasn't already preprocessed
total_preprocess_time_begin = datetime.now()
# Get the list of CSV files
csv_files = glob_get_files_list(input_files_path, file_format="csv")

# Preprocess the data
preprocess_data(csv_files, output_files_path_preprocessed_data, results_folder, timestamp, drop_protocols_and_ports=True)

# Update the list of CSV files
csv_files = glob_get_files_list(output_files_path_preprocessed_data, file_format="csv")

# Label all data inside CSV files
[read_and_label_data(file, data_folder, False) for file in csv_files]
total_preprocess_time_end = datetime.now()

print("[INFO] Running inference")
# Buid the PKL and CSV files lists
pkl_files = glob_get_files_list(models_folder, file_format="pkl")
inference_data_files = glob_get_files_list(data_folder, file_format="csv")

total_run_time_begin = datetime.now()
run_inference(pkl_files, inference_data_files)
total_run_time_end = datetime.now()
print("[INFO] Total preprocess run time:", (total_preprocess_time_end - total_preprocess_time_begin).total_seconds(), "(seconds)")
print("[INFO] Total inference run time:", (total_run_time_end - total_run_time_begin).total_seconds(), "(seconds)")
