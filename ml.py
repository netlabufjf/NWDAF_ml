import os
import pandas as pd
# import glob
from sklearn.preprocessing import MinMaxScaler

from util import glob_get_files_list,read_csv

# File paths
input_files_path = "./pcap/output/4-ML/preprocess/labeled_files/" # read CSV files from here
output_files_path_base = "./pcap/output/4-ML/" # save the output there
output_files_path_labeled_data = output_files_path_base + "preprocess/labeled_data/" # save the labeled output files there
output_files_path_preprocessed_data = output_files_path_base + "preprocess/data_ready_to_ml/" # save the labeled output files there

# Function to read and label data in CSV files
def read_and_label_data(file_path, out_dir, remove_old_files=False):
    # Read the CSV file
    file_name_without_path = file_path.split('/')[-1] # get old file name
    new_file_name_and_path = out_dir + os.path.splitext(file_name_without_path)[0] + "_labeled.csv"
    if not os.path.exists(new_file_name_and_path):
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
    else:
        print(f"[INFO] The file {file_name_without_path} was already labeled")

def categorical_data_to_dummy(file_path):
    df = read_csv(file_path)
    columns_to_exclude = ["Source_IP", "Destination_IP"] # TODO deal with these columns later (or leave them excluded)
    df = df.drop(columns=columns_to_exclude)
    df_dummies = pd.get_dummies(df)

    return df_dummies
    
def preprocess_data(files_path, output_dir):
    for i in files_path:
        file_name = i.split('/')[-1]
        out_file_path = output_dir + file_name
        if not os.path.exists(out_file_path):
            df = read_csv(i)
            print("[INFO] Working with", file_name)
            df = df.dropna(axis=1, how='all') # drop columns where all values are None
            df = categorical_data_to_dummy(df) # transform categorical features
            df.drop(columns=["Packet_no"], axis=1, inplace=True) # drop packet number to avoid using it in the models
            
            # Normalize features using standardization
            # using MinMax to avoid giving more importance to a given feature
            # for more information: https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html
            scaler = MinMaxScaler() 
            data_features_names = list(df)
            scaler.fit(df[data_features_names])
            df[data_features_names] = scaler.transform(df[data_features_names])

            # Save the normalized data
            df.to_csv(out_file_path, index=False)
            print("[INFO] Preprocessed data saved to:", out_file_path)
        else:
            print(f"[INFO] The file {file_name} was already preprocessed")


# Buid the CSV files list
csv_files = glob_get_files_list(input_files_path, "csv")

# Preprocess the data
preprocess_data(csv_files, output_files_path_preprocessed_data)

# Update the list of CSV files
csv_files = glob_get_files_list(output_files_path_preprocessed_data, "csv")

# Label all data inside CSV files
[read_and_label_data(file, output_files_path_labeled_data, False) for file in csv_files]


# TODO implement ML models

