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

from util import glob_get_files_list,read_csv,label_id_to_text

models_folder = "./pcap/output/4-ML/models/" # read the models from here
data_folder = "./pcap/output/4-ML/preprocess/labeled_data/" # read the inference data from here
results_folder = "./pcap/output/4-ML/inference_results/" # save the results here

# Buid the PKL and CSV files lists
pkl_files = glob_get_files_list(models_folder, "pkl")
inference_data_files = glob_get_files_list(data_folder, "csv")

def run_inference(models_file_list, inference_data_file_list):
    for file in inference_data_file_list:
        file_name = file.split('/')[-1]

        if 'inference' in file:
            print("[INFO] Running inference on", file_name)
            
            columns = ["file_name", "file_num_rows", "model_name",
                        "inference_result_label", "inference_result",
                        "accuracy", "precision", "recall", "f_score_class",
                        "inference_result_count_0", "inference_result_count_1", "inference_result_count_2",
                        "inf_pred_time_ms", "inf_total_time_ms"]
            # Initialize results_df with columns
            results_df = pd.DataFrame(columns=columns)
            
            data = read_csv(file) # load inference data
            data_num_rows = len(data)

            for path in models_file_list:
                total_inference_time_begin = time_ns()
                model = pickle.load(open(path, 'rb')) # load model from disk
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

                # Model evaluation data
                accuracy = accuracy_score(y_true, y_pred)
                cm = confusion_matrix(y_true, y_pred, labels=[0, 1, 2])
                precision = precision_score(y_true, y_pred, average="weighted", labels=[true_label])
                recall = recall_score(y_true, y_pred, average="weighted", zero_division=np.nan)
                f_score_class = f1_score(y_true, y_pred, average="weighted", labels=[true_label])

                # print("[DEBU] Accuracy:", round(accuracy, 10))
                # print(f"[DEBU] Confusion Matrix:\n{cm}")
                # print("[DEBU] Precision :", round(precision, 10))
                # print("[DEBU] Recall    :", round(recall, 10))
                # print("[DEBU] F1-score of class :", round(f_score_class, 10))
                # # TODO fix ROC AUC score
                # # if (model_name != "LinearSVC"): # LinearSVC doesn't implement proba
                # #     auc_score = roc_auc_score(y_true, model.predict_proba(inference_data), average='macro', multi_class='ovo', labels=[0, 1, 2])
                # #     print("[DEBU] ROC AUC Score :", round(auc_score, 10))
                # # else:
                # #     print("[DEBU] ROC AUC Score : Not calculated for", model_name)
                # #     auc_score = "N.A."
                
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
                    columns[9]: int(inference_result_counts[0]) if 0 in inference_result_counts else np.nan,
                    columns[10]: int(inference_result_counts[1]) if 1 in inference_result_counts else np.nan,
                    columns[11]: int(inference_result_counts[2]) if 2 in inference_result_counts else np.nan,
                    columns[12]: inference_pred_time,
                    columns[13]: total_inference_time,
                }
                
                # Add new row to the dataframe using loc[] method
                results_df.loc[len(results_df)] = new_row
                
            # Save the results dataframe to a CSV file with a unique filename based on the current time
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            # get the original input file name without format
            output_filename = file_name.split('/')[-1].split('_inference_')[0]
            results_df.to_csv(f"{results_folder}{output_filename}_{timestamp}_inference_results.csv", index=False)

        else:
            print(f"[WARN] Skipping file {file_name}")

total_run_time_begin = datetime.now()
run_inference(pkl_files, inference_data_files)
total_run_time_end = datetime.now()
print("[INFO] Total run time:", (total_run_time_end - total_run_time_begin).total_seconds(), "(seconds)")
