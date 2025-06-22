import yaml
import json
import logging
import pandas as pd
from utils import (
    read_excel_file,
    rename_columns,
    transform_and_structure_data,
    validate_data,
    connect_to_db,
    get_new_files,
    move_file,
    send_error_email,
    insert_record
)

def load_config(path="config.yaml"):
    """Loads the YAML configuration file."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        logging.error(f"Configuration file not found at {path}")
        return None
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        return None

def load_json_schema(path):
    """Loads a JSON schema file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"JSON schema file not found at {path}")
        return None
    except Exception as e:
        logging.error(f"Error loading JSON schema {path}: {e}")
        return None

def process_file(file_info: dict, config: dict, column_mapping: dict, fixed_schema: dict, descriptive_schema: dict, db_conn):
    """Processes a single file from SharePoint."""
    file_name = file_info['name']
    logging.info(f"Processing file: {file_name}")

    # --- Read file content from SharePoint ---
    df_raw = read_excel_file(file_info['content'])
    if df_raw is None:
        logging.error(f"Could not read Excel data from {file_name}.")
        # In a real scenario, you might want to send a different kind of notification
        # for a file that is fundamentally unreadable.
        move_file(config.get('sharepoint'), file_name, 'broken')
        return

    # --- Transformation ---
    df_renamed = rename_columns(df_raw, column_mapping)
    df_structured = transform_and_structure_data(df_renamed, list(fixed_schema.keys()))

    # --- Validation ---
    validation_errors = validate_data(df_structured, fixed_schema, descriptive_schema)

    # --- Loading ---
    if validation_errors:
        logging.error(f"Validation failed for {file_name}: {validation_errors}")
        send_error_email(config.get('notifications'), file_info['author'], file_name, validation_errors)
        move_file(config.get('sharepoint'), file_name, 'broken')
    else:
        logging.info(f"Validation successful for {file_name}. Inserting into database.")
        # For simplicity, we'll process each row in the validated DataFrame
        for record_to_insert in df_structured.to_dict(orient='records'):
            # Add metadata
            record_to_insert['login'] = file_info['author']
            record_to_insert['version'] = pd.Timestamp.now()
            
            insert_record(db_conn, record_to_insert)
        
        move_file(config.get('sharepoint'), file_name, 'imported')
        logging.info(f"Successfully processed and imported {file_name}.")

def main():
    """Main application entry point."""
    print("Starting Excel Importer application...")

    # Load configuration and schemas
    config = load_config()
    column_mapping = load_json_schema("columns_mapping.json")
    fixed_columns_schema = load_json_schema("fixed_columns.json")
    descriptive_data_schema = load_json_schema("descriptive_data.json")

    if not all([config, column_mapping, fixed_columns_schema, descriptive_data_schema]):
        print("Failed to load necessary configuration or schema files. Exiting.")
        return

    # --- Connect to External Services ---
    db_conn = connect_to_db(config.get('database'))
    if not db_conn:
        logging.critical("Could not establish database connection. Exiting.")
        return
    
    # --- Main Application Logic ---
    logging.info("Checking for new files...")
    new_files = get_new_files(config.get('sharepoint'))

    if not new_files:
        logging.info("No new files found.")
    else:
        for file_info in new_files:
            process_file(file_info, config, column_mapping, fixed_columns_schema, descriptive_data_schema, db_conn)

    print("Application finished.")

if __name__ == "__main__":
    # Basic logging configuration
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main() 