import logging
from utils import (
    load_config,
    load_schemas,
    find_excel_files,
    read_excel_files_to_dfs,
    validate_and_transform,
    export_dataframe_to_db,
    move_file_to_folder,
    format_error_report,
    send_error_email,
    log_event
)
import os

def main():
    # Step 1: Read configuration
    config = load_config()
    local_cfg = config['local']
    input_folder = local_cfg['input_folder']
    imported_folder = local_cfg['imported_folder']
    broken_folder = local_cfg['broken_folder']

    # Step 2: Load schemas
    column_mapping, fixed_schema, descriptive_schema = load_schemas()

    # Step 3: Find Excel files
    excel_files = find_excel_files(input_folder)
    if not excel_files:
        print(f"No Excel files found in {input_folder}. Exiting.")
        return

    # Step 4: Read Excel files
    dfs = read_excel_files_to_dfs(excel_files, input_folder)

    # Step 5: Validate and transform data
    combined_good_df, file_results = validate_and_transform(dfs, column_mapping, fixed_schema, descriptive_schema)

    # Step 6: Export to database
    export_dataframe_to_db(combined_good_df, config, logging)

    # Step 7: Move files to destination folders and handle errors
    for file, result in file_results.items():
        file_path = os.path.join(input_folder, file)
        if result["good_df"] is None or (result["bad_rows"] and len(result["bad_rows"]) > 0):
            # Send error report if there are bad rows
            if result["bad_rows"] and isinstance(result["bad_rows"], list) and result["bad_rows"] and isinstance(result["bad_rows"][0], dict):
                error_report = format_error_report(result["bad_rows"])
                send_error_email(None, file, error_report)
            move_file_to_folder(file_path, broken_folder)
            log_event(file, None, None, None, "ERROR", "move_file", "moved_to_broken")
        else:
            move_file_to_folder(file_path, imported_folder)
            log_event(file, None, None, None, "INFO", "move_file", "moved_to_imported")

    print("Phase 2 complete.")

if __name__ == "__main__":
    main() 