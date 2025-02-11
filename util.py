import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt
import os
from time import time_ns
from sklearn.preprocessing import MinMaxScaler,OrdinalEncoder
from imblearn.over_sampling import SMOTE

def read_csv(file_path):
    """
    A function to read CSV files

    Parameters
    ----------
        file_path : string
            A path that contains a CSV file to be read.

    Returns
    ----------
        pandas.DataFrame
            The df with the CSV content.
    """

    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
        return df
    except FileNotFoundError:
        print(f"[ERRO] File not found at path {file_path}")
        exit()
    except Exception as e:
        # printing stack trace 
        traceback.print_exception(*sys.exc_info())
        print("[ERRO]", type(e).__name__, e)
        exit()

def glob_get_files_list(path, file_format='*'):
    """
    A function to list files in a given directory

    Parameters
    ----------
        path : string
            A path that points to where the file list should be constructed from.
        file_format : string
            The format of the files to be listed. By default it reads any available.

    Returns
    ----------
        list
            The list of files found by glob.
    """
    files = glob.glob(path + '*.' + file_format)

    if not files: # check if glob is empty
            print("[ERRO] No files were read by glob. Please, check its parameters")
            exit()

    return files

def delete_files(file_name, path):
    """
    A function to delete a file from a given directory

    Parameters
    ----------
        file_name : string
            The file name that should be deleted.
        path : string
            A path that points to where the file should be deleted from.
    """
    file_path = path + file_name
    try:
        os.remove(file_path)
        print(f"[DEBU] File {file_name} has been deleted successfully from {path}") # DEBUG
    except FileNotFoundError:
        print(f"[ERRO] File in {file_path} not found")
    except PermissionError:
        print(f"[ERRO] Permission denied to delete the file {file_name} in {path}")
    except Exception as e:
        print(f"[ERRO] Error occurred while deleting the file: {e}")

def label_id_to_text(id):
    """
    A function to transform a label id to its textual name

    Parameters
    ----------
        id : int
            The id that should be returned.
    """
    # Assign label based on id
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

def plot_confusion_matrix(matrix, output_dir, data_input_file_name, model_name, operation_type='', timestamp='', save_plot=False, show_plot=True):
    """
    A function that plots a confusion matrix

    Parameters
    ----------
        matrix : numpy.ndarray
            The confusion matrix that should be plotted.
        output_dir: string
            The output path where the plot PDF file should be saved.
        data_input_file_name: string
            The name of the input file from where data was read from. To be used as part of the output name so it would be possible to differentiate between matrices from different data.
        model_name: string
            The name of the model to be used on the plot title and file name.
        operation_type: string
            A string that will be used on the plot title and file name. On our context, it should be "training" or "inference".
        timestamp: string
            A datetime-like formatted string that represents the time when this plot's data was created.
        save_plot: bool
            If the plot should be saved or not.
        show_plot: bool
            If the plot should be previewed or not.
    """
    # Plot confusion matrix as a heatmap
    font_size = 12
    # plt.figure(figsize=(8,6), dpi=300)
    # sns.set(font_scale=1.4)
    sns.heatmap(matrix, annot=True, fmt="d", cmap="Blues", xticklabels=[label_id_to_text(0), label_id_to_text(1), label_id_to_text(2)], 
                yticklabels=[label_id_to_text(0), label_id_to_text(1), label_id_to_text(2)],) #annot_kws={"size": font_size + 2})
    plt.title(f"{data_input_file_name}\nConfusion Matrix for {model_name} {operation_type}", fontsize=font_size)
    plt.xlabel("Predicted Label", fontsize=font_size)
    plt.ylabel("True Label", fontsize=font_size)

    if (save_plot):
        plt.savefig(f"{output_dir}{timestamp}_{data_input_file_name}_{model_name}_{operation_type}_confusion_matrix.pdf", dpi=300, bbox_inches='tight')
    elif (show_plot):
        plt.show() # DEBUG
    plt.close() # close figure to be able to plot other iterations correctly

def preprocess_data(files_path, preprocessed_data_output_dir, results_output_dir, timestamp):
    """
    A function to preprocess the data before labeling it and running the train and inference steps of the ML pipeline.

     Parameters
    ----------
        files_path: string
            A path that points to where the input files are located and should be read.
        preprocessed_data_output_dir: string
            The output path where the preprocessed data file should be saved.
        results_output_dir: string
            The output path where the results (e.g. file name, num of rows and process time) file should be saved.
        timestamp: string
            A datetime-like formatted string that represents the time when this plot's data was created.
    """
    columns_preprocess_time_df = ["file_name", "file_num_rows", "preprocess_time_ms", "preprocess_disk_time_ms", "preprocess_total_time_ms"]
    preprocess_time_df = pd.DataFrame(columns=columns_preprocess_time_df) # df to save the results

    for i in files_path:
        file_name = i.split('/')[-1]
        out_file_path = preprocessed_data_output_dir + file_name
        preprocess_time_begin = time_ns()

        if not os.path.exists(out_file_path):
            df = read_csv(i)
            data_num_rows = len(df)
            print("[INFO] Working with", file_name)

            # Drop some data
            # df = df.dropna(axis=1, how='all') # drop columns where all values are None
            # NOTE doing so was creating an inconsistent number of available features
            # which was expected, but most models I've tested can't handle this
            df.drop(columns=["Source_IP", "Destination_IP"], axis=1, inplace=True) # drop IP addresses to avoid using them in the models
            df.drop(columns=["Packet_no"], axis=1, inplace=True) # drop packet number to avoid using it in the models
            
            # Encode the categorical features
            feature_encoder = OrdinalEncoder()
            for col in df.columns:
                if col == "TCP_compl_str" or col == "TCP_flags_str" or col == "Frame_protocols":
                    df[col] = feature_encoder.fit_transform(df[[col]])
            
            # Change None (NaN type) to an int
            df.fillna(-1, inplace=True) # required by models like LR that can't handle NaN data
            # NOTE -1 is a valid int while not representing valid data (which starts with 0)
            # df.dropna(inplace=True) # not required for now (see "fillna line" above)

            # Normalize features using standardization
            # using MinMax to avoid giving more importance to a given feature
            # for more information: https://scikit-learn.org/stable/auto_examples/preprocessing/plot_all_scaling.html
            scaler = MinMaxScaler() 
            data_features_names = list(df)
            scaler.fit(df[data_features_names])
            df[data_features_names] = scaler.transform(df[data_features_names])
            preprocess_time_end = time_ns()

            # Save the normalized data
            preprocess_disk_time_begin = time_ns()
            df.to_csv(out_file_path, index=False)
            preprocess_disk_time_end = time_ns()
            print("[INFO] Preprocessed data saved to:", out_file_path)
            
            preprocess_disk_time_ms = (preprocess_disk_time_end - preprocess_disk_time_begin) / 10**6
            preprocess_time_ms = (preprocess_time_end - preprocess_time_begin) / 10**6
            preprocess_total_time_ms = (preprocess_time_ms + preprocess_disk_time_ms)

            new_row = {
                    columns_preprocess_time_df[0]: file_name,
                    columns_preprocess_time_df[1]: data_num_rows,
                    columns_preprocess_time_df[2]: preprocess_time_ms,
                    columns_preprocess_time_df[3]: preprocess_disk_time_ms,
                    columns_preprocess_time_df[4]: preprocess_total_time_ms,
                }
                
            # Add new row to the dataframe using loc[] method
            preprocess_time_df.loc[len(preprocess_time_df)] = new_row
        else:
            print(f"[INFO] The file {file_name} was already preprocessed")

    if len(preprocess_time_df) != 0:
        preprocess_time_df.to_csv(f"{results_output_dir}{timestamp}_preprocess_time.csv", index=False)

# Function to read and label data in CSV files
def read_and_label_data(file_path, out_dir, remove_old_files=False):
    """
    A function to label the data before running the train and inference steps of the ML pipeline.

     Parameters
    ----------
        file_path: string
            A path that points to where the input file is located on disk.
        out_dir: string
            A path where the labelled data should be stored on.
        remove_old_files: bool
            If True, the input file is deleted after processing.
    """
    # Read the CSV file
    file_name_without_path = file_path.split('/')[-1] # get old file name
    new_file_name_and_path = out_dir + os.path.splitext(file_name_without_path)[0] + "_labeled.csv"
    if not os.path.exists(new_file_name_and_path):
        df = pd.read_csv(file_path)
        
        # Assign labels based on filenames
        if 'embb' in file_path:
            label = 0
        elif 'urllc' in file_path:
            label = 1
        elif 'mmtc' in file_path:
            label = 2
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
            delete_files(file_name_without_path, file_path)
        
        print("[DEBU] Labeled data successfully saved to", new_file_name_and_path) # DEBUG
    else:
        print(f"[INFO] The file {file_name_without_path} was already labeled")

# Augment data using SMOTE
def data_augmentation(X_train, y_train):
    """
    A function that applies SMOTE to training data.

    Parameters
    ----------
        X_train: pandas.DataFrame
            Dataframe containing the training data split.
        y_train: pandas.Series
            Series containing the class labels from the training data split.
    
    Returns
    ----------
        pandas.DataFrame, pandas.Series
            The training data after applying the SMOTE resampling.
    """
    smote = SMOTE(sampling_strategy='not majority', random_state=42, k_neighbors=5)
    X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)

    return X_train_smote, y_train_smote
