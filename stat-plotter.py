import csv
import pandas as pd
import os
import matplotlib.pyplot as plt

from util import read_csv

# Create chart for each DataFrame
def plot_graph(df_to_plot, input_file_name, column_label, x_label, y_label, plt_type):
    for i, df in enumerate(df_to_plot):
        plt.figure(figsize=(10, 6)) # Set figure size
        
        # Adjust plot parameters according to each plot type
        if (plt_type == 'line'):
            plt.figure(figsize=(15, 6)) # Set figure size
            sorted_df = df.sort_values(by=column_label) # sort data before plotting
            plt.plot(sorted_df[column_label], sorted_df['count'], marker='.', linestyle=':')
        elif (plt_type == 'bar'):
            x = df[column_label]
            y = df['count'] # get the count column data
            labels = [str(x) for x in df[column_label]] # convert all labels to strings (required by plt.barh())
            total_count = y.sum()
            
            plt.bar(x, y, align='center')
            plt.xticks(x, labels, rotation=15)
            # Add the counts and percentages as labels above each bar
            for j in range(len(y)):
                percentage = round((y[j]/total_count)*100, 1)
                label_text = f"{y[j]} ({percentage}%)" # format the label text with both count and percentage
                plt.text(j, y[j], label_text, ha='center', va='bottom')
        else:
            print("[ERROR] Could not set plt_type correctly, currently it is:", plt_type)
            exit()
                
        plt.yscale('log')
        file_name_without_format = os.path.splitext(input_file_name[i])[0] # remove '.csv' from old file name
        plt.title(file_name_without_format)
        plt.xlabel(x_label)
        plt.ylabel(y_label + "(Logarithmic Scale)")
        plt.tight_layout()
        
        # Save plot
        output_file_path = os.path.join(output_files_path, f"{file_name_without_format}.pdf")
        plt.savefig(output_file_path, dpi=600, bbox_inches="tight")
        print(f"[INFO] Plots of {x_label} for {input_file_name[i]} have been saved") # TODO improve messages on screen

        # plt.show() # DEBUG
        plt.clf()  # clear the figure to create a new plot
        plt.close() # close each figure after finishing to free RAM

# File paths
input_files_path = "./pcap/output/2-stats/" # read CSV files from here
output_files_path = "./pcap/output/2-stats/graphs/" # save the output there

# Get file names and paths for protocol and length data
input_file_names_protocol = [f for f in os.listdir(input_files_path) if f.endswith('protocol.csv')]
input_file_paths_protocol = [os.path.join(input_files_path, f) for f in input_file_names_protocol]
input_file_names_length = [f for f in os.listdir(input_files_path) if f.endswith('len.csv')]
input_file_paths_length = [os.path.join(input_files_path, f) for f in input_file_names_length]

# Read CSV files
input_dfs_protocol = [read_csv(path) for path in input_file_paths_protocol]
input_dfs_length = [read_csv(path) for path in input_file_paths_length]

# Check if at least one file was found for each type
if not input_dfs_protocol and not input_dfs_length: # TODO improve this check to filter per type
    print(f"[ERROR] No CSV files found on {input_files_path}")
    exit()

# Create plots for both protocol and length data
plot_graph(input_dfs_protocol, input_file_names_protocol, '_ws.col.protocol', 'Protocol Label', 'Frequency', 'bar')
plot_graph(input_dfs_length, input_file_names_length, 'frame.len', 'Packet Length', 'Frequency', 'line')

print("[INFO] All plots have been finished")
