import pandas as pd
import io
import logging
import json
import datetime
import os

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

def validate_and_split_rows(df: pd.DataFrame, fixed_schema: dict, descriptive_schema: dict):
    """
    Validates each row and splits into good and bad rows with detailed errors.
    Returns (good_rows_df, bad_rows: list of dicts with row_num, errors, row_data)
    """
    good_rows = []
    bad_rows = []
    for idx, row in df.iterrows():
        errors = []
        # Fixed columns: presence/null/type
        for col, dtype in fixed_schema.items():
            if dtype == 'jsonb' or dtype == 'TIMESTAMP' or col == 'login':
                continue
            if col not in row or pd.isnull(row[col]):
                errors.append({
                    'row': idx+2, 'column': col, 'error': 'Missing value', 'value': None
                })
            elif dtype == 'DATETIME':
                if not pd.isnull(row[col]):
                    try:
                        pd.to_datetime(row[col])
                    except Exception:
                        errors.append({
                            'row': idx+2, 'column': col, 'error': 'Invalid date format', 'value': row[col]
                        })
        # Descriptive columns
        dane_opisowe = row.get('dane_opisowe', {})
        if not isinstance(dane_opisowe, dict):
            errors.append({'row': idx+2, 'column': 'dane_opisowe', 'error': 'Not a valid JSON object', 'value': str(dane_opisowe)})
        else:
            for key, value in dane_opisowe.items():
                if pd.isnull(value):
                    continue
                if key in descriptive_schema:
                    expected_type = descriptive_schema[key]
                    is_valid = False
                    if expected_type == 'boolean':
                        is_valid = isinstance(value, bool) or str(value).lower() in ['true', 'false', 'tak', 'nie', 'yes', 'no', '1', '0']
                    elif expected_type == 'float':
                        try:
                            float(value)
                            is_valid = True
                        except Exception:
                            is_valid = False
                    elif expected_type == 'string':
                        is_valid = isinstance(value, str)
                    elif expected_type == 'date':
                        try:
                            pd.to_datetime(value)
                            is_valid = True
                        except Exception:
                            is_valid = False
                    if not is_valid:
                        errors.append({'row': idx+2, 'column': key, 'error': f'Invalid type (expected {expected_type})', 'value': value})
        if errors:
            bad_rows.append({'row_num': idx+2, 'errors': errors, 'row_data': row.to_dict()})
        else:
            good_rows.append(row)
    good_df = pd.DataFrame(good_rows) if good_rows else pd.DataFrame(columns=df.columns)
    return good_df, bad_rows

def format_error_report(bad_rows):
    """Format a detailed error report for all bad rows."""
    lines = []
    for bad in bad_rows:
        row_num = bad['row_num']
        lines.append(f"Row {row_num}:")
        for err in bad['errors']:
            lines.append(f"  - Column: {err['column']}, Error: {err['error']}, Value: {err['value']}")
        lines.append(f"  Row data: {bad['row_data']}")
    return '\n'.join(lines)

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
def send_error_email(recipient, file_name, error_report):
    print(f"\n--- MOCK EMAIL TO: {recipient or 'user@example.com'} ---")
    print(f"Subject: Errors in file {file_name}")
    print("Body:")
    print(error_report)
    print("--- END EMAIL ---\n")

# --- Logging Functions ---
def log_event(file_name, id_type, id_value, product, level, action, result, extra=None):
    event = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "file_name": file_name,
        "id_type": id_type,
        "id_value": id_value,
        "product": product,
        "level": level,
        "action": action,
        "result": result
    }
    if extra:
        event.update(extra)
    print(json.dumps(event, ensure_ascii=False))

def merge_dane_opisowe(old, new):
    """Merge two descriptive data dicts, new values overwrite old."""
    merged = old.copy() if old else {}
    merged.update({k: v for k, v in new.items() if v is not None})
    return merged

def upsert_versioned_rows(good_df, output_path):
    """
    For each row in good_df, check if a record with the same (id_type, id_value, product) exists in output_path CSV.
    If so, merge dane_opisowe, create a new versioned row, and leave the old row unchanged.
    If not, add as new row with version.
    Returns a DataFrame of all rows to write (old + new versions).
    """
    if os.path.exists(output_path):
        existing = pd.read_csv(output_path)
        # Parse dane_opisowe from string to dict if needed
        if 'dane_opisowe' in existing.columns and existing['dane_opisowe'].dtype == object:
            existing['dane_opisowe'] = existing['dane_opisowe'].apply(lambda x: eval(x) if isinstance(x, str) and x.startswith('{') else x)
    else:
        existing = pd.DataFrame(columns=good_df.columns)
    all_rows = [r for _, r in existing.iterrows()]
    for _, row in good_df.iterrows():
        mask = (
            (existing['id_type'] == row['id_type']) &
            (existing['id_value'] == row['id_value']) &
            (existing['product'] == row['product'])
        ) if not existing.empty else pd.Series([False]*len(existing))
        if mask.any():
            old_row = existing[mask].iloc[-1]  # Use the latest
            old_dane = old_row['dane_opisowe'] if isinstance(old_row['dane_opisowe'], dict) else eval(old_row['dane_opisowe'])
            new_dane = row['dane_opisowe'] if isinstance(row['dane_opisowe'], dict) else eval(row['dane_opisowe'])
            merged_dane = merge_dane_opisowe(old_dane, new_dane)
            new_row = row.copy()
            new_row['dane_opisowe'] = merged_dane
            new_row['version'] = datetime.datetime.utcnow().isoformat() + "Z"
            all_rows.append(new_row)
        else:
            new_row = row.copy()
            new_row['version'] = datetime.datetime.utcnow().isoformat() + "Z"
            all_rows.append(new_row)
    return pd.DataFrame(all_rows)
