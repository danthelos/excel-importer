# Progress: Excel Data Importer

## What Works
- **Project Scaffolding**: All initial project files (`main.py`, `utils.py`, etc.) and configuration/schema files are in place.
- **Core Data Pipeline**: The data transformation and validation logic in `utils.py` is implemented.
- **Separated Test Runner**: A dedicated test script (`run_tests.py`) allows for local testing of the entire data pipeline, completely separate from the production application code (`main.py`).
- **Realistic Testing**: The test process reads from a physical Excel file (`test_data.xlsx`), providing a high-fidelity test of the import and parsing logic.
- **Negative Testing**: The test suite has been enhanced to include known-bad data in `test_data.xlsx`. The test runner (`run_tests.py`) now specifically verifies that these expected errors are caught, ensuring the validation logic is robust.
- **Phase 1: Local Import/Export**: The application now reads Excel files from a local folder, validates each row individually, exports all good rows to CSV, and collects detailed error info for all bad rows.
- **Detailed Error Reporting**: After processing each file, a detailed error report (per bad row, with all errors and row data) is generated and sent to a mocked email function for user notification.
- **Structured JSON Logging**: All process events (row import, validation, export, error, etc.) are now logged in JSON format compatible with ElasticSearch, including: `timestamp`, `file_name`, `id_type`, `id_value`, `product_type`, `level`, `action`, `result`. In Phase 1, logging occurs after CSV export; in Phase 2 (and beyond), logging occurs after successful or failed database export.
- **Partial Import**: Good rows are imported/exported even if some rows in the file are bad.
- **Successful Test Run**: The test script and main application have been successfully run against both valid and invalid data, proving the core logic works as expected.
- **Test Artifacts**: A `test_data.xlsx` file exists containing a mix of valid and invalid records.
- **Versioning/Merging Logic**: If a record (combination of `id_type`, `id_value`, `product_type`) already exists in the output CSV, the system merges `dane_opisowe`, creates a new versioned row, and leaves the old row unchanged.
- **Single Output CSV**: All good rows from all Excel files are now appended to a single output CSV (`output/data.csv`), not separate files per input. This simulates a database table for versioning and merging logic.
- **Configurable Data Directories**: All data directories (input, output, imported, broken) are now under `/data` and are configurable in `config.yaml`.
- **File Movement**: After processing, Excel files are moved to the `imported` folder on success or to the `broken` folder if there are any errors during import.
- **Test Code and Data Structure**: All test code and data are now located in the `/tests` directory (`tests/input`, `tests/output`, etc.), and `config.yaml` points to these locations.
- **Config Separation**: The main application uses `config.yaml` (with `data/` folders), while tests use `config.test.yaml` (with `tests/` folders). This ensures a clear separation between production and test environments.
- **Phase 2: Database Export**: The application now exports all validated, versioned data directly to a PostgreSQL database (table must already exist). All process events for DB export are logged. Data is validated before export.

## What's Left to Build

### Phase 1: Local File Processing
- (COMPLETE) Implement logic to read Excel files from a local folder.
- (COMPLETE) Validate and transform the data.
- (COMPLETE) Export all processed data from all Excel files to a single CSV file in a local folder (`output/data.csv`).
- (COMPLETE) Ensure robust error handling and logging for local operations.
- (COMPLETE) Support partial import and detailed error reporting per row.

### Phase 2: Database Export
- (COMPLETE) Replace CSV export with direct export to a PostgreSQL database.
- (COMPLETE) Ensure all database operations are robust and transactional.

### Phase 3: SharePoint Server 2019 Integration
- (COMPLETE) Implement logic to import files from a SharePoint Server 2019 document library.
- (COMPLETE) Continue exporting data to the database.
- (COMPLETE) Move processed files to 'imported' or 'broken' folders in SharePoint.
- (COMPLETE) Fallback to local folder logic if SharePoint config is not present.

### Phase 4: Workflow Orchestration and Schema API
- Integrate the workflow into Airflow for scheduled execution.
- Switch schema validation to use a REST API instead of a local file.

## Known Issues and Limitations
- **No Live Integration**: The application currently cannot connect to any real external services as all related functions are placeholders.
- **SharePoint API Uncertainty**: The exact methods for retrieving the "Created By" user from a file's metadata still need to be confirmed with a specific SharePoint client library during implementation.

## Evolution of Project Decisions
- **Initial State**: The project began with requirements documented in `prompt_eng.md`.
- **Formalize Knowledge**: The first action was to create the Memory Bank to structure all project information.
- **Separation of Test Logic**: The project was refactored to fully separate test execution (`run_tests.py`) from production code (`main.py`).
- **Negative Test Cases**: The testing strategy was evolved to include negative testing. The test data now includes invalid records, and the test runner asserts that these specific errors are correctly identified.
- **Realistic Test Data**: The test process uses a physical Excel file (`test_data.xlsx`) for all local testing.
- **Partial Import and Error Reporting**: Phase 1 was enhanced to support partial import of good rows, detailed per-row error reporting, and user notification via a mocked email function. 