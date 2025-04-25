import csv
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import time

from util import read_csv

def update_font_size(f_size):
    font_size = f_size # base font size
    # Update rcParams to make fonts larger
    plt.rcParams['font.size'] = font_size
    plt.rcParams['axes.labelsize'] = font_size + 2
    plt.rcParams['axes.titlesize'] = font_size + 4
    plt.rcParams['xtick.labelsize'] = font_size
    plt.rcParams['ytick.labelsize'] = font_size

# Create chart for each DataFrame
def plot_graph(df_to_plot, input_file_name, column_label, x_label, y_label, plt_type):
    for i, df in enumerate(df_to_plot):
        
        # Adjust plot parameters according to each plot type
        if (plt_type == 'dozens-of-bars'):
            plt.figure(figsize=(15, 6)) # Set figure size
            update_font_size(15)
            sorted_df = df.sort_values(by=column_label) # sort data before plotting
            # plt.plot(sorted_df[column_label], sorted_df['count'], marker='.', linestyle=':') # line plot
            plt.bar(sorted_df[column_label], sorted_df['count']) # bar plot
            
            # Calculate mean, median and mode
            mean_value = df['frame.len'].mean()
            median_value = df['frame.len'].median()
            mode_value = df['frame.len'][0]

            # Statistical bars configuration
            bar_max_height = sorted_df['count'].max() # get the highest height value on the plot 
            text_x_pos = 0.05 # x axis text anchor
            text_y_pos = 0.95 # y axis text anchor
            # set the colors
            mean_color = 'red'
            median_color = 'green'
            mode_color = 'purple'

            # Plot mean, median and mode as colored bars
            plt.bar(mean_value, bar_max_height, color=mean_color, alpha=0.5, width=3)
            plt.bar(median_value, bar_max_height, color=median_color, alpha=0.5, width=3)
            plt.bar(mode_value, bar_max_height, color=mode_color, alpha=0.5, width=3)

            # Annotate the plot with mean, median and mode values
            plt.text(text_x_pos, text_y_pos, f'Mean: {mean_value:.2f}', transform=plt.gca().transAxes, ha='left', va='top', color=mean_color)
            plt.text(text_x_pos, (text_y_pos - 0.05), f'Median: {median_value:.2f}', transform=plt.gca().transAxes, ha='left', va='top', color=median_color)
            plt.text(text_x_pos, (text_y_pos - 0.10), f'Mode: {mode_value}', transform=plt.gca().transAxes, ha='left', va='top', color=mode_color)

            # Adjust the grid and x axis labels
            plt.xticks(np.arange(0, 1505, 50), rotation=30)
            plt.grid(visible=True, axis='y', linestyle = '--', zorder=0)

        elif (plt_type == 'a-few-bars'):
            plt.figure(figsize=(10, 6)) # Set figure size
            update_font_size(12)
            x = df[column_label]
            y = df['count'] # get the count column data
            labels = [str(x) for x in df[column_label]] # convert all labels to strings (required by plt.barh())
            total_count = y.sum()

            # Map each xlabel to a specific color
            protocol_labels_list = ["UDP", 
                                    "ICMPv6",
                                    "TCP", "TCP, HiPerConTracer",
                                    "TLSv1.3", "TLSv1.2", "TLSv1", 
                                    "SSLv2", "SSL",
                                    "H1",
                                    "HTTP", "HTTP/JSON",
                                    "DNS",
                                    "QUIC",
                                    "PNIO",
                                    "OCSP"]
            color_labels = ['blue',
                            'purple', 
                            'green', 'green',
                            'orange', 'orange', 'orange',
                            'black', 'black',
                            'magenta',
                            'brown', 'brown',
                            'pink',
                            'grey',
                            'teal',
                            'cyan']
            label_to_color = {label: color for label, color in zip(protocol_labels_list, color_labels)}
            bar_colors = [label_to_color[label] for label in labels]
            
            plt.bar(x, y, align='center', color=bar_colors, label=labels)
            plt.xticks(x, labels, rotation=15)
            
            # Offsets tailored for the used dataset
            # they were obtained via trial and error
            if (y.max() > 1000):
                lim_upper_offset = 4.0
            else:
                lim_upper_offset = 1.5
            lim_bottom_offset = 1.4

            plt.ylim(y.min() / lim_bottom_offset, lim_upper_offset * y.max()) # adjust the bars to avoid plotting text out of bounds
            # Add the counts and percentages as labels above each bar
            for j in range(len(y)):
                percentage = round((y[j]/total_count)*100, 1)
                label_text = f"{y[j]}\n({percentage}%)" # format the label text with both count and percentage
                plt.text(j, y[j], label_text, ha='center', va='bottom')
        else:
            print("[ERROR] Could not set plt_type correctly, currently it is:", plt_type)
            exit()
                
        plt.yscale('log')
        file_name_without_format = os.path.splitext(input_file_name[i])[0] # remove '.csv' from old file name
        plt.title(file_name_without_format)
        plt.xlabel(x_label)
        plt.ylabel(y_label + " (Logarithmic Scale)")
        plt.tight_layout()
        
        # Save plot
        output_file_path = os.path.join(output_files_path, f"{file_name_without_format}.pdf")
        plt.savefig(output_file_path, dpi=600, bbox_inches="tight")
        print(f"[INFO] Plots of {x_label} for {input_file_name[i]} have been saved") # TODO improve messages on screen

        # plt.show() # DEBUG
        plt.clf()  # clear the figure to create a new plot
        plt.close() # close each figure after finishing to free RAM

def plot_time_series(dfs_to_plot, input_file_name, x_column_label, y_column_label, x_label, y_label):
    for i, df in enumerate(dfs_to_plot):
        plt.figure(figsize=(15, 6)) # Set figure size
        plt.plot(df[x_column_label], df[y_column_label], marker='.', linestyle=':')
        file_name_without_format = os.path.splitext(input_file_name[i])[0] # remove '.csv' from old file name
        plt.title(file_name_without_format)
        plt.xlabel(x_label + " (seconds)")
        plt.ylabel(y_label)
        plt.tight_layout()
        
        # Save plot
        output_file_path = os.path.join(output_files_path, f"{file_name_without_format}.pdf")
        plt.savefig(output_file_path, dpi=120, bbox_inches="tight")
        print(f"[INFO] Plots of {x_label} for {input_file_name[i]} have been saved") # TODO improve messages on screen

        # plt.show() # DEBUG
        plt.clf()  # clear the figure to create a new plot
        plt.close() # close each figure after finishing to free RAM

# File paths
input_files_path = "./pcap/output/2-stats/" # read CSV files from here
output_files_path = "./pcap/output/2-stats/graphs/" # save the output there

start_time = time.time() # record the start of execution
# Get file names and paths for protocol and length data
input_file_names_protocol = [f for f in os.listdir(input_files_path) if f.endswith('protocol.csv')]
input_file_paths_protocol = [os.path.join(input_files_path, f) for f in input_file_names_protocol]
input_file_names_length = [f for f in os.listdir(input_files_path) if f.endswith('len.csv')]
input_file_paths_length = [os.path.join(input_files_path, f) for f in input_file_names_length]
input_file_names_frame_time_number = [f for f in os.listdir(input_files_path) if f.endswith('time_series.csv')]
input_file_paths_frame_time_number = [os.path.join(input_files_path, f) for f in input_file_names_frame_time_number]

# Read CSV files
input_dfs_protocol = [read_csv(path) for path in input_file_paths_protocol]
input_dfs_length = [read_csv(path) for path in input_file_paths_length]
input_dfs_time_series = [read_csv(path) for path in input_file_paths_frame_time_number]

# Check if at least one file was found for each type
# TODO improve this check to filter per type
if (not input_dfs_protocol and not input_dfs_length and not input_dfs_time_series): 
    print(f"[ERROR] No CSV files found on {input_files_path}")
    exit()

# Create plots for both protocol and length data
plot_graph(input_dfs_protocol, input_file_names_protocol, '_ws.col.protocol', 'Protocol Label', 'Frequency', 'a-few-bars')
plot_graph(input_dfs_length, input_file_names_length, 'frame.len', 'Packet Length (bytes)', 'Frequency', 'dozens-of-bars')
plot_time_series(input_dfs_time_series, input_file_names_frame_time_number, 'frame.time_relative', 'frame.number', 'Packet Capture Time', 'Packet Number')

print("[INFO] All plots have been finished")
end_time = time.time() # record the end of execution
print(f"[DEBU] Execution time: {end_time - start_time} s")
