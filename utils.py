import pandas as pd
import io
import logging

# This file will contain all the core functions for the Excel Importer application.

# --- Data Processing Functions ---
def read_excel_file(file_content: bytes):
    """
    Reads the content of an Excel file from bytes into a pandas DataFrame.
    
    Args:
        file_content (bytes): The byte content of the .xlsx file.
        
    Returns:
        pd.DataFrame or None: A DataFrame containing the Excel data, or None if an error occurs.
    """
    try:
        # Use a BytesIO object to allow pandas to read the byte stream as if it were a file
        return pd.read_excel(io.BytesIO(file_content))
    except Exception as e:
        logging.error(f"Failed to read or parse Excel file: {e}")
        return None

def rename_columns(df: pd.DataFrame, column_mapping: dict):
    """
    Renames DataFrame columns based on the provided mapping.

    Args:
        df (pd.DataFrame): The input DataFrame with original column names.
        column_mapping (dict): A dictionary mapping original names to new names.

    Returns:
        pd.DataFrame: A new DataFrame with renamed columns.
    """
    df_renamed = df.copy()
    mappable_columns = {k: v for k, v in column_mapping.items() if k in df_renamed.columns}
    df_renamed.rename(columns=mappable_columns, inplace=True)
    return df_renamed

def transform_and_structure_data(df: pd.DataFrame, fixed_columns: list):
    """
    Applies business rules and structures the DataFrame for database import.

    Args:
        df (pd.DataFrame): The DataFrame with renamed columns.
        fixed_columns (list): A list of column names that are considered fixed data.

    Returns:
        pd.DataFrame: A new DataFrame with a 'dane_opisowe' jsonb column.
    """
    df_structured = df.copy()

    if 'product' in df_structured.columns:
        df_structured['product'].fillna('all', inplace=True)

    fixed_cols_in_df = [col for col in fixed_columns if col in df_structured.columns and col != 'dane_opisowe']
    descriptive_cols = [col for col in df_structured.columns if col not in fixed_cols_in_df]
    df_structured['dane_opisowe'] = df_structured[descriptive_cols].to_dict(orient='records')
    df_final = df_structured.drop(columns=descriptive_cols)
    return df_final

def validate_data(df: pd.DataFrame, fixed_schema: dict, descriptive_schema: dict):
    """
    Validates the DataFrame against fixed and descriptive schemas.

    Args:
        df (pd.DataFrame): The transformed DataFrame to validate.
        fixed_schema (dict): Schema for the required fixed columns.
        descriptive_schema (dict): Schema for the descriptive data columns.

    Returns:
        list: A list of error messages. An empty list means validation passed.
    """
    errors = []
    
    # 1. Validate fixed columns (presence, nulls, and type)
    required_fixed_cols = [col for col, dtype in fixed_schema.items() if dtype != 'jsonb' and dtype != 'TIMESTAMP' and col != 'login']
    
    for col in required_fixed_cols:
        if col not in df.columns:
            errors.append(f"Missing required fixed column: '{col}'")
            continue # Can't check a column that doesn't exist

        # Check for nulls in required columns
        null_rows = df[df[col].isnull()]
        for index, row in null_rows.iterrows():
            errors.append(f"Row {index+2}: Missing value in required fixed column '{col}'.")

    # Check data types for specific fixed columns
    date_cols = {col: dtype for col, dtype in fixed_schema.items() if dtype == "DATETIME"}
    for col in date_cols:
        if col in df.columns:
            # Use pd.to_datetime with errors='coerce' which turns invalid dates into NaT
            # Then find rows where the original value was not null but the converted one is
            original_not_null = df[col].notna()
            converted_is_null = pd.to_datetime(df[col], errors='coerce').isna()
            invalid_date_rows = df[original_not_null & converted_is_null]

            for index, row in invalid_date_rows.iterrows():
                errors.append(f"Row {index+2}: Column '{col}' has invalid date format. Value is '{row[col]}'.")

    # 2. Validate descriptive data within the 'dane_opisowe' JSON column
    for index, row in df.iterrows():
        descriptive_data = row.get('dane_opisowe', {})
        if not isinstance(descriptive_data, dict):
            errors.append(f"Row {index+2}: 'dane_opisowe' is not a valid JSON object.")
            continue

        for key, value in descriptive_data.items():
            if pd.isnull(value):
                continue

            if key in descriptive_schema:
                expected_type_str = descriptive_schema[key]
                is_valid = False
                if expected_type_str == 'boolean':
                    is_valid = isinstance(value, bool) or str(value).lower() in ['true', 'false', 'tak', 'nie', 'yes', 'no', '1', '0']
                elif expected_type_str == 'float':
                    try:
                        float(value)
                        is_valid = True
                    except (ValueError, TypeError): is_valid = False
                elif expected_type_str == 'string':
                    is_valid = isinstance(value, str)
                elif expected_type_str == 'date':
                    try:
                        pd.to_datetime(value)
                        is_valid = True
                    except (ValueError, TypeError): is_valid = False
                
                if not is_valid:
                    errors.append(f"Row {index+2}: Column '{key}' has invalid type. Expected '{expected_type_str}', got '{type(value).__name__}'.")
    return errors

# --- Database Functions (Placeholders) ---
def connect_to_db(db_config):
    logging.info("Attempting to connect to the database... (Placeholder)")
    return "mock_connection"

def find_existing_record(db_conn, record):
    logging.info(f"Checking for existing record... (Placeholder)")
    return None

def insert_record(db_conn, record):
    logging.info(f"Inserting new record... (Placeholder)")
    return True

# --- SharePoint Functions (Placeholders) ---
def get_new_files(sp_config):
    logging.info("Checking for new files in SharePoint... (Placeholder)")
    return [{"name": "sample_data.xlsx", "content": b"", "author": "test.user@example.com"}]

def move_file(sp_config, file_name, destination):
    logging.info(f"Moving file '{file_name}' to '{destination}' folder... (Placeholder)")
    return True

# --- Notification Functions (Placeholders) ---
def send_error_email(smtp_config, recipient, file_name, errors):
    logging.info(f"Sending error email to {recipient} for file {file_name}... (Placeholder)")
    return True

# --- Logging Functions ---
# (e.g., setup_logger)
