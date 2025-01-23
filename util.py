import pandas as pd

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
