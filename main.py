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
    log_event,
    get_new_files,
    move_file
)
import os

CONFIG_FILE = "config.yaml"

def main():
    # Step 1: Read configuration
    config = load_config(CONFIG_FILE)
    local_cfg = config['local']
    input_folder = local_cfg['input_folder']
    imported_folder = local_cfg['imported_folder']
    broken_folder = local_cfg['broken_folder']
    sharepoint_cfg = config.get('sharepoint')

    # Step 2: Load schemas
    column_mapping, fixed_schema, descriptive_schema = load_schemas()

    # Step 3: Try SharePoint import first if config is present
    if sharepoint_cfg:
        sp_files = get_new_files(sharepoint_cfg)
        if not sp_files:
            message = f"No Excel files found in SharePoint library."
            log_event(
                file_name=None,
                id_type=None,
                id_value=None,
                product_type=None,
                level="INFO",
                action="get_new_files",
                result="no_files_found",
                extra={"message": message}
            )
            print(message)
            return
        dfs = {}
        for file in sp_files:
            try:
                df = read_excel_file(file['content'])
                dfs[file['name']] = df
            except Exception as e:
                log_event(file['name'], None, None, None, "ERROR", "read_excel", "error", {"message": str(e)})
                continue
        combined_good_df, file_results = validate_and_transform(dfs, column_mapping, fixed_schema, descriptive_schema)
        export_dataframe_to_db(combined_good_df, config, logging)
        for file, result in file_results.items():
            if result["good_df"] is None or (result["bad_rows"] and len(result["bad_rows"]) > 0):
                if result["bad_rows"] and isinstance(result["bad_rows"], list) and result["bad_rows"] and isinstance(result["bad_rows"][0], dict):
                    error_report = format_error_report(result["bad_rows"])
                    send_error_email(None, file, error_report)
                move_file(sharepoint_cfg, file, "broken")
                log_event(file, None, None, None, "ERROR", "move_file", "moved_to_broken")
            else:
                move_file(sharepoint_cfg, file, "imported")
                log_event(file, None, None, None, "INFO", "move_file", "moved_to_imported")
        print("Phase 3 complete (SharePoint import).")
        return

    # Step 4: Fallback to local folder logic
    excel_files = find_excel_files(input_folder)
    if not excel_files:
        message = f"No Excel files found in {input_folder}. Exiting."
        log_event(
            file_name=None,
            id_type=None,
            id_value=None,
            product_type=None,
            level="INFO",
            action="find_excel_files",
            result="no_files_found",
            extra={"message": message}
        )
        print(message)
        return
    dfs = read_excel_files_to_dfs(excel_files, input_folder)
    combined_good_df, file_results = validate_and_transform(dfs, column_mapping, fixed_schema, descriptive_schema)
    export_dataframe_to_db(combined_good_df, config, logging)
    for file, result in file_results.items():
        file_path = os.path.join(input_folder, file)
        if result["good_df"] is None or (result["bad_rows"] and len(result["bad_rows"]) > 0):
            if result["bad_rows"] and isinstance(result["bad_rows"], list) and result["bad_rows"] and isinstance(result["bad_rows"][0], dict):
                error_report = format_error_report(result["bad_rows"])
                send_error_email(None, file, error_report)
            move_file_to_folder(file_path, broken_folder)
            log_event(file, None, None, None, "ERROR", "move_file", "moved_to_broken")
        else:
            move_file_to_folder(file_path, imported_folder)
            log_event(file, None, None, None, "INFO", "move_file", "moved_to_imported")
    print("Phase 2 complete (Local import).")

if __name__ == "__main__":
    main() 