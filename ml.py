import os
import pandas as pd
# import glob

from util import glob_get_files_list

# File paths
input_files_path = "./pcap/output/4-ML/preprocess/labeled_files/" # read CSV files from here
output_files_path_base = "./pcap/output/4-ML/" # save the output there
output_files_path_labeled_data = output_files_path_base + "preprocess/labeled_data/" # save the labeled output files there

# Function to read and label data in CSV files
def read_and_label_data(file_path, remove_old_files=False):
    # Read the CSV file
    df = pd.read_csv(file_path)
    
    # Assign labels based on filenames
    if 'embb' in file_path:
        label = 1
    elif 'urllc' in file_path:
        label = 2
    elif 'mmtc' in file_path:
        label = 3
    else:
        raise ValueError(f"Could not determine label from filename {file_path}")
        exit()
    
    file_name_without_path = file_path.split('/')[-1] # get old file name
    new_file_name_and_path = output_files_path_labeled_data + os.path.splitext(file_name_without_path)[0] + "_labeled.csv"
    
    # Add label to DataFrame
    print(f"[INFO] Labeling {file_name_without_path} ... ", end='')
    df['label'] = label
    df.to_csv(new_file_name_and_path, index=False)
    print("[ OK ]")

    # if storage space is constrained, update remove_old_files to True to free some space
    if (remove_old_files):
        try:
            os.remove(file_path)
            print(f"[DEBU] File '{file_path}' has been deleted successfully.") # DEBUG
        except FileNotFoundError:
            print(f"[ERRO] File in '{file_path}' not found.")
        except PermissionError:
            print(f"[ERRO] Permission denied to delete the file in '{file_path}'.")
        except Exception as e:
            print(f"[ERRO] Error occurred while deleting the file: {e}")
    
    print("[DEBU] Labeled data successfully saved to", new_file_name_and_path) # DEBUG


# List of CSV files
csv_files = glob_get_files_list(input_files_path, "csv")

# Label all data inside CSV files
[read_and_label_data(file, False) for file in csv_files]

# TODO read the labeled data
# TODO implement ML models
