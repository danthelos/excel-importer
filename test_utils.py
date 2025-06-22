import pandas as pd
import logging

def load_test_excel_to_dataframe(file_path: str = "test_data.xlsx"):
    """
    Reads the test Excel file and loads it into a pandas DataFrame.
    
    Args:
        file_path (str): The path to the test Excel file.
        
    Returns:
        pd.DataFrame or None: A DataFrame with the test data, or None if an error occurs.
    """
    try:
        df = pd.read_excel(file_path)
        logging.info(f"Successfully loaded test data from '{file_path}'.")
        return df
    except FileNotFoundError:
        logging.error(f"Test data file not found at '{file_path}'.")
        return None
    except Exception as e:
        logging.error(f"Error reading test data file '{file_path}': {e}")
        return None 