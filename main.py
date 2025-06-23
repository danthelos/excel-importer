import os
import yaml
import json
import logging
import pandas as pd
from utils import (
    read_excel_file,
    rename_columns,
    transform_and_structure_data,
    validate_and_split_rows,
    format_error_report,
    send_error_email,
    log_event,
    upsert_versioned_rows
)

def load_config(path="config.yaml"):
    """Loads the YAML configuration file."""
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        return None

def load_json_schema(path):
    """Loads a JSON schema file."""
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading JSON schema {path}: {e}")
        return None

def process_local_excel_file(file_path, config, column_mapping, fixed_schema, descriptive_schema):
    file_name = os.path.basename(file_path)
    logging.info(f"Processing file: {file_name}")
    try:
        with open(file_path, "rb") as f:
            file_content = f.read()
        df_raw = read_excel_file(file_content)
        if df_raw is None:
            logging.error(f"Could not read Excel data from {file_name}. Skipping.")
            log_event(file_name, None, None, None, "ERROR", "read_excel", "error", {"message": "Could not read Excel data"})
            return False
        df_renamed = rename_columns(df_raw, column_mapping)
        df_structured = transform_and_structure_data(df_renamed, list(fixed_schema.keys()))
        good_df, bad_rows = validate_and_split_rows(df_structured, fixed_schema, descriptive_schema)
        # Log each row event
        for idx, row in df_structured.iterrows():
            id_type = row.get('id_type')
            id_value = row.get('id_value')
            product = row.get('product')
            is_good = not any(bad['row_num'] == idx+2 for bad in bad_rows)
            if is_good:
                log_event(file_name, id_type, id_value, product, "INFO", "validate_row", "success")
            else:
                bad = next(b for b in bad_rows if b['row_num'] == idx+2)
                log_event(file_name, id_type, id_value, product, "ERROR", "validate_row", "error", {"errors": bad['errors']})
        # Versioning/merging logic before CSV export
        output_folder = config['local']['output_folder']
        os.makedirs(output_folder, exist_ok=True)
        output_path = os.path.join(output_folder, file_name.replace('.xlsx', '.csv'))
        if not good_df.empty:
            all_rows = upsert_versioned_rows(good_df, output_path)
            all_rows.to_csv(output_path, index=False)
            logging.info(f"Exported {len(good_df)} new versioned rows to {output_path}")
            for _, row in good_df.iterrows():
                log_event(file_name, row.get('id_type'), row.get('id_value'), row.get('product'), "INFO", "export_row", "success", {"output_path": output_path})
        else:
            logging.info(f"No valid rows to export for {file_name}.")
        # Prepare and send error report for bad rows
        if bad_rows:
            error_report = format_error_report(bad_rows)
            logging.error(f"{len(bad_rows)} bad rows found in {file_name}. Sending error report...")
            send_error_email(None, file_name, error_report)
        return True
    except Exception as e:
        logging.error(f"Error processing {file_name}: {e}")
        log_event(file_name, None, None, None, "ERROR", "process_file", "error", {"message": str(e)})
        return False

def main():
    """Main application entry point."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    print("Starting Excel Importer Phase 1 (Local Folder Mode)...")
    config = load_config()
    if not config:
        print("Failed to load config. Exiting.")
        return
    column_mapping = load_json_schema("columns_mapping.json")
    fixed_schema = load_json_schema("fixed_columns.json")
    descriptive_schema = load_json_schema("descriptive_data.json")
    if not all([column_mapping, fixed_schema, descriptive_schema]):
        print("Failed to load necessary schema files. Exiting.")
        return
    local_cfg = config['local']
    input_folder = local_cfg['input_folder']
    output_folder = local_cfg['output_folder']
    imported_folder = local_cfg['imported_folder']
    broken_folder = local_cfg['broken_folder']
    for folder in [input_folder, output_folder, imported_folder, broken_folder]:
        os.makedirs(folder, exist_ok=True)
    output_path = os.path.join(output_folder, "data.csv")
    excel_files = [f for f in os.listdir(input_folder) if f.lower().endswith('.xlsx')]
    if not excel_files:
        print(f"No Excel files found in {input_folder}. Exiting.")
        return
    all_good_rows = []
    for file in excel_files:
        file_path = os.path.join(input_folder, file)
        file_name = os.path.basename(file_path)
        logging.info(f"Processing file: {file_name}")
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()
            df_raw = read_excel_file(file_content)
            if df_raw is None:
                logging.error(f"Could not read Excel data from {file_name}. Skipping.")
                log_event(file_name, None, None, None, "ERROR", "read_excel", "error", {"message": "Could not read Excel data"})
                # Move to broken
                os.rename(file_path, os.path.join(broken_folder, file_name))
                continue
            df_renamed = rename_columns(df_raw, column_mapping)
            df_structured = transform_and_structure_data(df_renamed, list(fixed_schema.keys()))
            good_df, bad_rows = validate_and_split_rows(df_structured, fixed_schema, descriptive_schema)
            # Log each row event
            for idx, row in df_structured.iterrows():
                id_type = row.get('id_type')
                id_value = row.get('id_value')
                product = row.get('product')
                is_good = not any(bad['row_num'] == idx+2 for bad in bad_rows)
                if is_good:
                    log_event(file_name, id_type, id_value, product, "INFO", "validate_row", "success")
                else:
                    bad = next(b for b in bad_rows if b['row_num'] == idx+2)
                    log_event(file_name, id_type, id_value, product, "ERROR", "validate_row", "error", {"errors": bad['errors']})
            if not good_df.empty:
                all_good_rows.append(good_df)
            # Prepare and send error report for bad rows
            if bad_rows:
                error_report = format_error_report(bad_rows)
                logging.error(f"{len(bad_rows)} bad rows found in {file_name}. Sending error report...")
                send_error_email(None, file_name, error_report)
                # Move to broken
                os.rename(file_path, os.path.join(broken_folder, file_name))
                continue
            # If no errors, move to imported
            os.rename(file_path, os.path.join(imported_folder, file_name))
        except Exception as e:
            logging.error(f"Error processing {file_name}: {e}")
            log_event(file_name, None, None, None, "ERROR", "process_file", "error", {"message": str(e)})
            # Move to broken
            try:
                os.rename(file_path, os.path.join(broken_folder, file_name))
            except Exception:
                pass
            continue
    # After all files, upsert/merge all good rows into a single output CSV
    if all_good_rows:
        combined_good_df = pd.concat(all_good_rows, ignore_index=True)
        all_rows = upsert_versioned_rows(combined_good_df, output_path)
        all_rows.to_csv(output_path, index=False)
        logging.info(f"Exported {len(combined_good_df)} new versioned rows to {output_path}")
        for _, row in combined_good_df.iterrows():
            log_event("data.csv", row.get('id_type'), row.get('id_value'), row.get('product'), "INFO", "export_row", "success", {"output_path": output_path})
    else:
        logging.info(f"No valid rows to export from any file.")
    print("Phase 1 complete.")

if __name__ == "__main__":
    main() 