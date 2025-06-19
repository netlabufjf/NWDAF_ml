import pandas as pd
import time
from subprocess import check_call
from sklearn.tree import DecisionTreeClassifier,export_graphviz
from sklearn.model_selection import train_test_split
from util import (glob_get_files_list,
                  read_csv)

# File paths
working_folder = "./pcap/output/4-ML/"
output_files_path_labeled_data = working_folder + "preprocess/labeled_data/" # save the labeled output files there
# Vars
class_names_list = ["eMBB","URLLC","mMTC"]
features_names_list = []
start_time = time.time() # record the start of execution

# Load and prepare splits from labeled training data
def read_and_split_train_data(csv_file_list, split, with_features_names=False):
    training_data = pd.DataFrame()
    for file in csv_file_list:
        if 'training' in file:
            df = read_csv(file)
            training_data = pd.concat([training_data, df], ignore_index=True)
        elif 'inference' in file:
            # print("[DEBU] Skipped inference file found at", file) # DEBUG
            pass
        else:
            raise ValueError(f"[ERRO] Could not determine data set type from filename {file}")
            exit()

    # Prepare data for supervised learning
    X = training_data.drop('label', axis=1)  # Features
    y = training_data['label']  # Target variable

    if (split):
        # Now X and y are ready for supervised learning
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

        if (with_features_names):
            feature_list = list(X.columns)

            return X_train, X_test, y_train, y_test, feature_list
        else:
            return X_train, X_test, y_train, y_test

    else:
        return X, y

# Create the DT visualization plots
def create_and_plot_tree_visualization(file_name_suffix, rounded_rectangles, horizontal, print_percentages, parallel_leaves=False):
    file_path_without_format = "img/dtree_" + file_name_suffix
    dot_file_path = file_path_without_format + ".dot"
    png_file_path = file_path_without_format + ".png"
    pdf_file_path = file_path_without_format + ".pdf"

    print(f"[INFO] Exporting {dot_file_path} ... ", end='')
    export_graphviz(dt, out_file=dot_file_path, class_names=class_names_list, feature_names=features_names_list, 
                   rounded=rounded_rectangles, rotate=horizontal, proportion=print_percentages, leaves_parallel=parallel_leaves)
    # For more parameters see: https://scikit-learn.org/stable/modules/generated/sklearn.tree.export_graphviz.html
    print(" [ OK ] ")

    print(f"[INFO] Plotting {file_path_without_format} ... ", end='')
    # check_call(['dot', '-Tpng', dot_file_path, '-o', png_file_path]) # save as PNG
    check_call(['dot', '-Tpdf', dot_file_path, '-o', pdf_file_path]) # save as PDF
    print(" [ OK ] ")

print("[INFO] Loading files and creating the model ... ", end='')

# Update the list of CSV files
csv_files = glob_get_files_list(output_files_path_labeled_data, "csv")

# Create the splits
X_train, X_test, y_train, y_test, features_names_list = read_and_split_train_data(csv_files, True, True)

dt = DecisionTreeClassifier() # default parameter DT
# dt = DecisionTreeClassifier(max_depth=4) # a first parameter that could be adjusted is the tree depth
# dt = DecisionTreeClassifier(min_samples_leaf=1000, min_samples_split=10000)
# dt = DecisionTreeClassifier(max_depth=6, min_samples_leaf=1000, min_samples_split=10000)
# For more parameters see: https://scikit-learn.org/stable/modules/generated/sklearn.tree.DecisionTreeClassifier.html
dt.fit(X_train, y_train)
print(" [ OK ] ")


# Plot "normal" tree (default parameters + rounded boxes)
create_and_plot_tree_visualization("vertical_raw", True, False, False)
# Plot "normal" tree paralell leaves
create_and_plot_tree_visualization("vertical_leaves", True, False, False, True)
# Plot "normal" tree with percentages
create_and_plot_tree_visualization("vertical_percentages", True, True, True)

# Plot horizontal tree with numerical values
create_and_plot_tree_visualization("horizontal_raw", True, True, False)
# Plot horizontal tree with numerical values
create_and_plot_tree_visualization("horizontal_leaves", True, True, False, True)
# Plot horizontal tree with percentages
create_and_plot_tree_visualization("horizontal_percentages", True, True, True)
print("[INFO] Plotting has finished successfully")
end_time = time.time() # record the end of execution
print(f"[DEBU] Execution time: {end_time - start_time} s")
