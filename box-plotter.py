import pandas as pd
import matplotlib.pyplot as plt

from util import glob_get_files_list

# File paths
input_files_path = "./pcap/output/3-JSON-export/" # read CSV files from here
output_files_path = "./pcap/output/3-JSON-export/box-plots/" # save the output there

def plot_box_plot(file_path):
    # Read the CSV file
    df = pd.read_csv(file_path)
    input_file_name = file_path.split('/')[-1].split('.')[0]
    
    # If needed, drop some columns
    # df.drop(columns=["TCP_window_size"], axis=1, inplace=True) # drop TCP window size because of its size
    
    df.boxplot(vert=False, figsize=(6,8))
    plt.title(input_file_name + ' box plot')
    plt.xscale("symlog")
    # plt.subplots_adjust(left=0.28)
    plt.tight_layout()
    # Reference for the layout adjustment: https://stackoverflow.com/a/18500068

    full_output_path = output_files_path + input_file_name + '.pdf'
    plt.savefig(full_output_path, bbox_inches='tight', pad_inches=0, dpi=120)
    print("[INFO] Box plot sucessfully saved on", full_output_path)
    
    # plt.show() # DEBUG
    plt.close() # close each figure after finishing to enable multiple runs

# List of CSV files
csv_files = glob_get_files_list(input_files_path, "csv")

for i in csv_files:
    try:
        plot_box_plot(i)
    except AssertionError as e:
        print("[ERRO] Could not parse", i, "due to", e)
        # TODO fix AssertionError too