# Active Context: Excel Data Importer

## Current Work Focus
Phase 1 is now functionally complete. The application reads all Excel files from a local folder, validates each row individually, and appends all good rows from all files to a single CSV file (`output/data.csv`). This simulates a database table for versioning and merging logic. Detailed error info for all bad rows is collected and sent in a report to a mocked email function. The focus is now on preparing for Phase 2 (database export) and gathering feedback on the local workflow.

## Recent Changes
- **Single Output CSV**: All good rows from all Excel files are now appended to a single output CSV (`output/data.csv`), not separate files per input. This better simulates a database table and supports versioning/merging across files.
- **Partial Import and Error Reporting**: The application supports partial import of good rows, detailed per-row error reporting, and user notification via a mocked email function.
- **Versioning/Merging Logic**: If a record (combination of `id_type`, `id_value`, `product`) already exists in the output CSV, the system merges `dane_opisowe`, creates a new versioned row, and leaves the old row unchanged.
- **Detailed Logging**: All errors are logged with row number, column, error type, value, and full row data.
- **Successful Test Run**: The main application has been successfully run against both valid and invalid data, with correct export and error reporting.
- **Configurable Data Directories**: All data directories (input, output, imported, broken) are now under `/data` and their paths are configurable via `config.yaml`.
- **File Movement**: After processing, Excel files are moved to the `imported` folder on success or to the `broken` folder if there are any errors during import.
- **Test Code and Data Structure**: All test code and data are now located in the `/tests` directory (`tests/input`, `tests/output`, etc.), and `config.yaml` points to these locations.
- **Config Separation**: The main application uses `config.yaml` (with `data/` folders), while tests use `config.test.yaml` (with `tests/` folders). This ensures a clear separation between production and test environments.

## Next Steps
1.  **Prepare for Phase 2: Database Export**:
    - Refactor the export logic to support writing to a PostgreSQL database instead of CSV.
    - Ensure transactional integrity and error handling for database operations.
2.  **Phase 3: SharePoint Server 2019 Integration**:
    - Implement logic to import files from a SharePoint Server 2019 document library.
3.  **Phase 4: Airflow and Schema API**:
    - Integrate the workflow into Airflow and switch schema validation to use a REST API.

## Active Decisions and Considerations
- **User Feedback**: The detailed error report is designed to be user-friendly and actionable, supporting future email notification workflows.
- **Incremental Complexity**: The phased approach continues to allow for early testing and validation of core logic before introducing external dependencies.
- **Local Testing**: All logic in Phase 1 is easily testable without any network or database dependencies.

## Important Patterns and Preferences
- **Modularity**: Each phase is implemented in a way that allows for easy extension or replacement in subsequent phases.
- **Type Hinting**: Maintain strict type hinting for all new code.
- **Defensive Coding**: All new code that interacts with files or external systems must be wrapped in `try...except` blocks.

## Learnings and Project Insights
- Per-row validation and partial import provide a much better user experience and data quality than all-or-nothing imports.
- Detailed, actionable error reporting is essential for user adoption and smooth operation.
- The phased, testable approach is working well and will make future integrations easier. 