import csv
import traceback
import sys
import pandas as pd
import os

def read_csv(file_path):
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"[ERROR] File not found at path {file_path}")
        exit()
    except Exception as e:
        # printing stack trace 
        traceback.print_exception(*sys.exc_info())
        print("[ERROR]", type(e).__name__, e)
        exit()

def extract_frequency_info(data_frames, column_names):
    freq_data_list = []
    
    for df in data_frames:
        try:
            # Use value_counts to get the frequency of each unique value in the specified columns
            frequency_info = {column: df[column].value_counts() for column in column_names}
            freq_data_list.append(frequency_info)
        except KeyError as ke:
            missing_columns = [col for col in column_names if col not in df.columns]
            print(f"Error: Columns {missing_columns} not found in the DataFrame.")
            exit()
        except Exception as e:
            # printing stack trace 
            traceback.print_exception(*sys.exc_info())
            print("[ERROR]", type(e).__name__, e)
            exit()

    return freq_data_list

def print_frequency_data(freq_data_list):
    for counter, item in enumerate(freq_data_list, start=1):
        print("[INFO] Frequency data extracted from data frame number", counter)
        for column_name, freq_series in item.items():
            print(f"Frequency information for {column_name}:")
            print(freq_series)
            file_name_without_format = os.path.splitext(input_files_names[counter - 1])[0] # remove '.csv' from old file name
            freq_series.to_csv(os.path.join(output_files_path, file_name_without_format + "." + column_name + ".csv"))
        print("[INFO] Finished printing data frame", counter)

# File paths
input_files_path = "./pcap/output/1-PCAP-export/" # read CSV files from here
output_files_path = "./pcap/output/2-stats/" # save the output there

# get the list of all CSV files in the input directory
input_files_names = [f for f in os.listdir(input_files_path) if f.endswith('.csv')]
# input_files_names = [f for f in os.listdir(input_files_path) if f.endswith('test.csv') | f.endswith('5g1.csv')] # initial tests
# create a list of file paths by joining the input directory path with each file name
input_file_paths = [os.path.join(input_files_path, f) for f in input_files_names]
# TODO create an option menu to choose which file(s) to use on next steps

# Read CSV files
input_dfs = [read_csv(path) for path in input_file_paths]

# check if at least one file was found
if len(input_dfs) == 0:
    print(f"[ERROR] No CSV file found on {input_files_path}")
    exit()

# Extract frequency information
# as the features are the same on all files, no need to do that for all of them
column_names = input_dfs[0].columns.tolist()
# removes some columns from the frequency calculation because they almost always have only unique values
columns_to_remove = ["frame.number", "frame.time_relative", "_ws.col.info"]

for col in columns_to_remove:
    column_names.remove(col)

input_freq_data_list = extract_frequency_info(input_dfs, column_names)

# Print frequency information
print("[INFO] Printing data frequency information")
print_frequency_data(input_freq_data_list)
print("[INFO] Finished printing data frequency information")
