import pandas as pd
import numpy as np
import pickle

from datetime import datetime
from util import glob_get_files_list,read_csv

models_folder = "./pcap/output/4-ML/models/" # read the models from here
data_folder = "./pcap/output/4-ML/preprocess/labeled_data/" # read the inference data from here
results_folder = "./pcap/output/4-ML/inference_results/" # save the results here

# Buid the PKL and CSV files lists
pkl_files = glob_get_files_list(models_folder, "pkl")
inference_data_files = glob_get_files_list(data_folder, "csv")

def label_id_to_text(id):
    # Assign labels based on id
    if id == 0:
        label = 'eMBB'
    elif id == 1:
        label = 'URLLC'
    elif id == 2:
        label = 'mMTC'
    else:
        raise ValueError(f"Could not determine label from id {id}")
        exit()
    return label

def run_inference(models_file_list, inference_data_file_list):
    for file in inference_data_file_list:
        file_name = file.split('/')[-1]

        if 'inference' in file:
            print("[INFO] Running inference on", file_name)
            
            # Initialize results_df with columns
            results_df = pd.DataFrame(columns=["file_name", "model_name", "inference_result_label", "inference_result", "inference_result_count_0", "inference_result_count_1", "inference_result_count_2"])
            
            data = read_csv(file) # load inference data

            for path in models_file_list:
                model = pickle.load(open(path, 'rb')) # load model from disk
                model_name = model.__class__.__name__ 
                print("[INFO] Using", model_name)
                
                inference_data = data.drop('label', axis=1)  # remove the label column
                
                y_pred = model.predict(inference_data)
                inference_result = pd.Series([model.classes_[i] for i in y_pred])
                inference_result_counts = inference_result.value_counts()
                    # print("[DEBU] Inference result:", inference_result.idxmax())  # DEBUG
                
                inference_result_label = label_id_to_text(inference_result_counts.idxmax())

                new_row = {
                    "file_name": file_name,
                    "model_name": model_name,
                    "inference_result_label": inference_result_label,
                    "inference_result": inference_result_counts.idxmax(),
                    "inference_result_count_0": inference_result_counts[0] if 0 in inference_result_counts else np.nan,
                    "inference_result_count_1": inference_result_counts[1] if 1 in inference_result_counts else np.nan,
                    "inference_result_count_2": inference_result_counts[2] if 2 in inference_result_counts else np.nan
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

run_inference(pkl_files, inference_data_files)
