import logging
import pandas as pd
from utils import (
    rename_columns,
    transform_and_structure_data,
    validate_data,
)
from test_utils import load_test_excel_to_dataframe
from main import load_json_schema

def run_test_pipeline():
    """
    Runs the data processing pipeline using local test data.
    """
    logging.info("--- Starting Test Run ---")

    # Load schemas needed for processing
    column_mapping = load_json_schema("columns_mapping.json")
    fixed_schema = load_json_schema("fixed_columns.json")
    descriptive_schema = load_json_schema("descriptive_data.json")

    if not all([column_mapping, fixed_schema, descriptive_schema]):
        logging.critical("Failed to load necessary schema files for testing. Aborting.")
        return

    # 1. Load test data from Excel file
    df_raw = load_test_excel_to_dataframe()
    if df_raw is None:
        logging.error("Failed to load test data. Aborting test run.")
        return
    
    logging.info(f"Successfully loaded {len(df_raw)} rows from test file.")

    # 2. Run transformation logic
    df_renamed = rename_columns(df_raw, column_mapping)
    df_structured = transform_and_structure_data(df_renamed, list(fixed_schema.keys()))
    logging.info("Data transformation complete.")
    # print(df_structured.to_markdown()) # Optional: uncomment to see the transformed data

    # 3. Run validation logic
    validation_errors = validate_data(df_structured, fixed_schema, descriptive_schema)
    logging.info("Data validation complete.")

    # 4. Report results
    expected_errors = [
        "Row 4: Missing value in required fixed column 'id_type'.",
        "Row 5: Column 'data_od' has invalid date format. Value is 'not a date'.",
        "Row 7: Column 'taxi' has invalid type. Expected 'boolean', got 'str'."
    ]

    # Check if all expected errors were found
    found_all_expected = all(any(expected in error for error in validation_errors) for expected in expected_errors)
    
    # Check if there were any unexpected errors
    unexpected_errors = [error for error in validation_errors if not any(expected in error for expected in expected_errors)]

    if found_all_expected and not unexpected_errors:
        logging.info("--- Test PASSED ---")
        logging.info("Successfully caught all expected validation errors and no unexpected errors were found.")
        logging.info("The 'not known key' column was correctly ignored as per the requirements.")
    else:
        logging.error("--- Test FAILED ---")
        if not found_all_expected:
            logging.error("Did not find all expected errors. Missing:")
            for expected in expected_errors:
                if not any(expected in error for error in validation_errors):
                    logging.error(f"- {expected}")
        if unexpected_errors:
            logging.error("Found unexpected errors:")
            for error in unexpected_errors:
                logging.error(f"- {error}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    run_test_pipeline() 