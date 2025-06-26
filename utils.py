import pandas as pd
import io
import logging
import json
import datetime
import os
from sqlalchemy import create_engine, Table, MetaData
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
import requests
from requests_ntlm import HttpNtlmAuth
import smtplib
from email.mime.text import MIMEText

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

def transform_and_structure_data(df: pd.DataFrame, fixed_columns: list, descriptive_schema: dict):
    """
    Applies business rules and structures the DataFrame for database import.

    Args:
        df (pd.DataFrame): The DataFrame with renamed columns.
        fixed_columns (list): A list of column names that are considered fixed data.
        descriptive_schema (dict): The schema dict for allowed descriptive columns.

    Returns:
        pd.DataFrame: A new DataFrame with a 'dane_opisowe' jsonb column.
    """
    df_structured = df.copy()

    if 'product_type' in df_structured.columns:
        df_structured['product_type'].fillna('all', inplace=True)

    fixed_cols_in_df = [col for col in fixed_columns if col in df_structured.columns and col != 'dane_opisowe']
    # Only include descriptive columns that are present in the descriptive schema
    descriptive_cols = [col for col in df_structured.columns if col not in fixed_cols_in_df and col in descriptive_schema]
    df_structured['dane_opisowe'] = df_structured[descriptive_cols].apply(lambda row: clean_and_filter_dane_opisowe(row.to_dict()), axis=1)
    # Drop all columns that are not fixed columns or dane_opisowe
    cols_to_keep = fixed_cols_in_df + ['dane_opisowe']
    df_final = df_structured[cols_to_keep]
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

# --- SharePoint Functions (Placeholders) ---
def _build_folder_url(shp_url, folder_name):
    # Remove trailing slash if present and append folder name
    if not shp_url.endswith("/"):
        shp_url += "/"
    return f"{shp_url}{folder_name}/Files"

def get_new_files(sp_config):
    """
    Fetch new Excel files from the source_folder in SharePoint (on-prem) via REST API.
    Returns a list of dicts: {"name": ..., "content": ..., "author": ..., "author_email": ...}
    """
    shp_url = sp_config["library_url"]
    source_folder = sp_config["source_folder"]
    username = sp_config["user_login"]
    password = sp_config["user_password"]
    results = []
    auth = HttpNtlmAuth(username, password)
    headers = {"Accept": "application/json;odata=verbose"}
    folder_url = _build_folder_url(shp_url, source_folder)
    try:
        response = requests.get(folder_url, auth=auth, headers=headers)
        response.raise_for_status()
        data = response.json()
        for file in data['d']['results']:
            if file['Name'].lower().endswith(".xlsx"):
                file_url = file['_metadata']['uri']
                file_response = requests.get(file_url, auth=auth, headers=headers)
                file_content = file_response.content if file_response.status_code == 200 else None
                # Fetch author information
                author_url = f"{file_url}/Author"
                author_response = requests.get(author_url, auth=auth, headers=headers)
                author = None
                author_email = None
                if author_response.status_code == 200:
                    author_data = author_response.json()
                    author = author_data['d'].get('Title', None)
                    author_email = author_data['d'].get('Email', None)
                results.append({
                    "name": file['Name'],
                    "content": file_content,
                    "author": author,
                    "author_email": author_email
                })
        logging.info(f"Found {len(results)} Excel files in SharePoint.")
    except requests.RequestException as e:
        logging.error(f"Error accessing SharePoint: {e}")
    return results

def move_file(sp_config, file_name, destination_folder_key):
    """
    Move a file in SharePoint to the specified folder (imported or broken) via REST API.
    destination_folder_key: 'imported_folder' or 'broken_folder' from config
    """
    import os
    username = sp_config["user_login"]
    password = sp_config["user_password"]
    shp_url = sp_config["library_url"]
    source_folder = sp_config["source_folder"]
    dest_folder = sp_config[destination_folder_key]
    auth = HttpNtlmAuth(username, password)
    headers = {"Accept": "application/json;odata=verbose"}
    # Build REST URLs
    src_url = _build_folder_url(shp_url, source_folder).replace("/Files", f"/{file_name}")
    dest_url = _build_folder_url(shp_url, dest_folder).replace("/Files", f"/{file_name}")
    move_api_url = f"{src_url}/moveTo?newurl='{dest_url}',flags=1"
    try:
        response = requests.post(move_api_url, auth=auth, headers=headers)
        if response.status_code in (200, 204):
            logging.info(f"Moved file '{file_name}' to '{dest_folder}' in SharePoint.")
            return True
        else:
            logging.error(f"Error moving file '{file_name}' in SharePoint: {response.status_code} {response.text}")
            return False
    except requests.RequestException as e:
        logging.error(f"Error moving file '{file_name}' in SharePoint: {e}")
        return False

# --- Notification Functions (Placeholders) ---
def send_error_email(config, recipient, file_name, error_report):
    notifications = config.get('notifications', {})
    smtp_server_address = notifications.get('smtp_server_address', 'localhost:25')
    from_addr = notifications.get('from', 'somerecipient@domain.com')
    sending_enabled = notifications.get('sending_email_enabled', False)
    subject_prefix = notifications.get('subject_prefix', 'This is email from system X')
    
    subject = f"{subject_prefix} - Błąd importu pliku {file_name}"
    to_addr = recipient or from_addr
    body = error_report
    msg = MIMEText(body, _charset="utf-8")
    msg['Subject'] = subject
    msg['From'] = from_addr
    msg['To'] = to_addr

    log_message = f"EMAIL TO: {to_addr}\nSUBJECT: {subject}\nBODY:\n{body}"
    # Always log the email content
    logging.info(f"[EMAIL-CONTENT] {log_message}")
    if not sending_enabled:
        logging.info(f"[EMAIL-LOG-ONLY] {log_message}")
        return
    try:
        server_host, server_port = smtp_server_address.split(":")
        with smtplib.SMTP(server_host, int(server_port)) as server:
            server.sendmail(from_addr, [to_addr], msg.as_string())
        logging.info(f"[EMAIL-SENT] {log_message}")
    except Exception as e:
        logging.error(f"[EMAIL-ERROR] Failed to send email: {e}\n{log_message}")

# --- Logging Functions ---
def log_event(file_name, id_type, id_value, product_type, level, action, result, extra=None):
    event = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "file_name": file_name,
        "id_type": id_type,
        "id_value": id_value,
        "product_type": product_type,
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

def clean_and_filter_dane_opisowe(d):
    # Remove keys with NaN or empty values from dane_opisowe dict
    return {k: v for k, v in d.items() if v not in [None, "", float('nan')] and not (isinstance(v, float) and pd.isna(v))}

def export_dataframe_to_db(dataframe, config, logger):
    if dataframe.empty:
        logger.info("No valid rows to export to database.")
        return
    db_cfg = config['database']
    db_url = f"postgresql://{db_cfg['user_login']}:{db_cfg['user_password']}@{db_cfg['host']}:{db_cfg['port']}/{db_cfg['db_name']}"
    engine = create_engine(db_url)
    metadata = MetaData()
    schema_name = db_cfg.get('schema', 'blacklist')
    table_name = db_cfg.get('table', 'entity')
    with engine.connect() as connection:
        table = Table(table_name, metadata, schema=schema_name, autoload_with=engine)
        logger.info(f"Exporting {len(dataframe)} rows to database table '{schema_name}.{table_name}'...")
        for _, row in dataframe.iterrows():
            data = row.to_dict()
            if 'dane_opisowe' in data and isinstance(data['dane_opisowe'], str):
                import ast
                try:
                    data['dane_opisowe'] = ast.literal_eval(data['dane_opisowe'])
                except Exception:
                    pass
            # Clean and filter dane_opisowe before inserting
            if 'dane_opisowe' in data:
                data['dane_opisowe'] = clean_and_filter_dane_opisowe(data['dane_opisowe'])
            try:
                with connection.begin():
                    stmt = insert(table).values(**data)
                    connection.execute(stmt)
                    logger.info(f"Row exported: {data}")
            except IntegrityError:
                logger.warning(f"Integrity conflict for row: {data}")
            except Exception as ex:
                logger.error(f"Error exporting row: {ex}, data: {data}")
                raise
        logger.info(f"All rows exported to database table '{schema_name}.{table_name}'.")

def load_config(config_path):
    import yaml
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def load_schemas():
    with open("columns_mapping.json", 'r', encoding='utf-8') as f:
        column_mapping = json.load(f)
    with open("fixed_columns.json", 'r', encoding='utf-8') as f:
        fixed_schema = json.load(f)
    with open("descriptive_data.json", 'r', encoding='utf-8') as f:
        descriptive_schema = json.load(f)
    return column_mapping, fixed_schema, descriptive_schema

def find_excel_files(input_folder):
    return [f for f in os.listdir(input_folder) if f.lower().endswith('.xlsx')]

def read_excel_files_to_dfs(excel_files, input_folder):
    dfs = {}
    for file in excel_files:
        file_path = os.path.join(input_folder, file)
        with open(file_path, "rb") as f:
            file_content = f.read()
        df = read_excel_file(file_content)
        dfs[file] = df
    return dfs

def validate_and_transform(dfs, column_mapping, fixed_schema, descriptive_schema):
    all_good_rows = []
    file_results = {}
    for file, df_raw in dfs.items():
        if df_raw is None:
            file_results[file] = {"good_df": None, "bad_rows": ["Could not read Excel data"]}
            continue
        df_renamed = rename_columns(df_raw, column_mapping)
        df_structured = transform_and_structure_data(df_renamed, list(fixed_schema.keys()), descriptive_schema)
        good_df, bad_rows = validate_and_split_rows(df_structured, fixed_schema, descriptive_schema)
        file_results[file] = {"good_df": good_df, "bad_rows": bad_rows}
        if not good_df.empty:
            all_good_rows.append(good_df)
    if all_good_rows:
        combined_good_df = pd.concat(all_good_rows, ignore_index=True)
    else:
        combined_good_df = pd.DataFrame()
    return combined_good_df, file_results

def move_file_to_folder(file_path, dest_folder):
    os.makedirs(dest_folder, exist_ok=True)
    file_name = os.path.basename(file_path)
    dest_path = os.path.join(dest_folder, file_name)
    os.rename(file_path, dest_path)
    return dest_path
