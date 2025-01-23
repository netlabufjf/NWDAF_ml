import pandas as pd
import glob

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
