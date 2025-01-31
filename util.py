import pandas as pd
import glob
import seaborn as sns
import matplotlib.pyplot as plt

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

def plot_confusion_matrix(matrix, output_dir, model_name, operation_type='', timestamp='', save_plot=False, show_plot=True):
    """
    A function that plots a confusion matrix

    Parameters
    ----------
        matrix : ?
            The confusion matrix that should be plotted.
        output_dir: string
            The output path where the plot PDF file should be saved.
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
    plt.title(f"Confusion Matrix for {model_name} {operation_type}", fontsize=font_size)
    plt.xlabel("Predicted Label", fontsize=font_size)
    plt.ylabel("True Label", fontsize=font_size)

    if (save_plot):
        plt.savefig(f"{output_dir}{timestamp}_{model_name}_{operation_type}_confusion_matrix.pdf", dpi=300, bbox_inches='tight')
    elif (show_plot):
        plt.show() # DEBUG
    plt.close() # close figure to be able to plot other iterations correctly
