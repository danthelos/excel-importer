# Project Brief: Excel Data Importer

## Overview
This project involves creating a Python application to automatically import data from Excel files and process them through several development phases, starting with local file operations and culminating in full enterprise integration with SharePoint Server 2019 and Airflow.

## Core Requirements

### Phase 1: Local File Processing
- Read Excel files from a local folder.
- Validate and transform the data as per business rules.
- Export the processed data to a CSV file in a local folder.
- **Log all process events in JSON format compatible with ElasticSearch after successful CSV export (Phase 1).**
- In Phase 1, all good rows from all Excel files in the input folder are appended to a single output CSV file (`output/data.csv`). This simulates a database table and supports versioning/merging logic across files. There are no per-file CSV exports.
- If a record (combination of `id_type`, `id_value`, `product_type`) already exists in the output CSV:
  - Retrieve the `dane_opisowe` column from the old record
  - Create a new record with an updated `version` (timestamp)
  - Merge the old and new descriptive data (new values overwrite old keys)
  - Leave the old record unchanged (append the new version as a new row)
- All data directories (input, output, imported, broken) are under `/data` and are configurable in `config.yaml`.
- After processing, Excel files are moved to the `imported` folder on success or to the `broken` folder if there are any errors during import.
- All test code and data are now located in the `/tests` directory (`tests/input`, `tests/output`, etc.), and `config.yaml` points to these locations.
- The main application uses `config.yaml` (with `data/` folders), while tests use `config.test.yaml` (with `tests/` folders). This ensures a clear separation between production and test environments.

### Phase 2: Database Export
- Instead of exporting to a CSV, export the processed data directly to a PostgreSQL database.
- **Log all process events in JSON format compatible with ElasticSearch after successful or failed data export to the database.**
- In Phase 2, the application exports all validated, versioned data directly to a PostgreSQL database (table must already exist). All process events for DB export are logged. Data is validated before export.
- **Important: The database table must allow multiple records with the same (id_type, id_value, product_type). There must NOT be a primary key or unique constraint on these columns. This is required to support versioning/history as per the business logic.**
- **When constructing `dane_opisowe` for each row, any key with a NaN or empty value must be omitted from the JSON for that row. Only valid, non-empty descriptive data should be stored in the database.**
- **When constructing `dane_opisowe`, only columns present in the descriptive schema are included. Any column not listed in the schema is ignored and not added to the JSON.**

### Phase 3: SharePoint Server 2019 Integration
- Import Excel files from a SharePoint Server 2019 document library (not Office 365/SharePoint Online).
- Continue exporting data to the database.

### Phase 4: Workflow Orchestration and Schema API
- Integrate the mechanism into an Airflow DAG for scheduled execution.
- Validate descriptive data using a REST API for schema validation (instead of a local file).
- **Implement email notifications:** If there are problems with importing an Excel file, send an email notification to the file's author (as specified in the requirements). This is not yet implemented and is required for project completion.

## Goals
- Start with a simple, testable local workflow and incrementally add complexity.
- Ensure robust data validation and error handling at every phase.
- Provide clear separation between local, database, and enterprise integrations.
- Maintain a testable, modular codebase throughout all phases.

## Project Scope

### In Scope
- Building the application in incremental phases as described above.
- Local file operations, database integration, SharePoint Server 2019 integration, and Airflow orchestration.
- Data validation, transformation, and error notification logic.

### Out of Scope
- Office 365/SharePoint Online integration.
- Manual data entry or UI development.
- Database and SharePoint server setup/administration.
- Schema API implementation (it is an external service to be consumed). 