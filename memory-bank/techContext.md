# Tech Context: Excel Data Importer

## Technologies Used
- **Programming Language**: Python 3.x
- **Phase 1: Local File Operations**:
  - `pandas`, `openpyxl`: For reading Excel files from a local folder and exporting to CSV.
  - Standard Python libraries for file I/O and error handling.
- **Phase 2: Database Export**:
  - `psycopg2-binary`: For PostgreSQL interaction.
- **Phase 3: SharePoint Server 2019 Integration**:
  - A Python library for SharePoint Server 2019 (on-premises) integration (e.g., `Office365-REST-Python-Client` or a compatible alternative for SP2019).
- **Phase 4: Workflow Orchestration and Schema API**:
  - `apache-airflow`: For workflow orchestration.
  - `requests`: For REST API schema validation.
- **Configuration Format**: YAML
- **Data Interchange Format**: JSON (for `dane_opisowe` and logs), CSV (for local export)

## Development Setup
1.  **Environment**: Create and activate a Python virtual environment (e.g., `python -m venv .venv`).
2.  **Dependencies**: Install all required packages using `pip install -r requirements.txt`.
3.  **Configuration**:
    - Create a `config.yaml` file from a provided template.
    - Populate it with valid credentials and paths for your local folders, database, and (in later phases) SharePoint and Airflow.
4.  **Local Folders**: For Phase 1, create input and output folders for Excel and CSV files.
5.  **Database Schema**: For Phase 2 and beyond, ensure the `blacklist.entity` table exists in the PostgreSQL database with the correct schema.
6.  **SharePoint Folders**: For Phase 3, ensure access to a SharePoint Server 2019 document library.
7.  **Airflow (Phase 4)**: A local Airflow instance (e.g., via Docker Compose) will be required for developing and testing the DAG.

## Technical Constraints
- **Local-First**: All logic in Phase 1 must work without any network or database dependencies.
- **Incremental Integration**: Each phase should be independently testable before moving to the next.
- **SharePoint Server 2019**: Integration must use the correct API for on-premises SharePoint, not Office 365/SharePoint Online.
- **Statelessness**: The application itself must be stateless. All state is maintained externally in files, the database, or SharePoint.
- **Database Versioning**: The database table must allow multiple records with the same (id_type, id_value, product_type). There must NOT be a primary key or unique constraint on these columns. This is required to support versioning/history as per the business logic.

## Dependencies
- **pandas**, **openpyxl**: For Excel and CSV operations.
- **psycopg2-binary**: For PostgreSQL (Phase 2+).
- **SharePoint Client Library**: For SharePoint Server 2019 integration (Phase 3).
- **apache-airflow**: For workflow orchestration (Phase 4).
- **requests**: For REST API schema validation (Phase 4).

## Tool Usage Patterns
- **Version Control**: Git should be used for all code changes. A feature-branch workflow is recommended.
- **Dependency Management**: All Python dependencies must be explicitly listed with their versions in a `requirements.txt` file to ensure reproducible builds.
- **Configuration**: All environment-specific variables, credentials, and endpoints **must** be managed in the `config.yaml` file. There should be no hardcoded secrets in the source code.
- **Logging**: The standard `logging` library should be configured at the start of the application to output structured JSON. This ensures that logs are machine-readable and can be easily ingested by services like ElasticSearch.
- **Structured JSON Logging**: All process events (row import, validation, export, error, etc.) are logged in JSON format compatible with ElasticSearch, including: `timestamp`, `file_name`, `id_type`, `id_value`, `product_type`, `level`, `action`, `result`. In Phase 1, logging occurs after CSV export; in Phase 2 (and beyond), logging occurs after successful or failed database export.
- **Test Utils**: `test_utils.py` is used for generating mock data for local testing.

## Data Schemas and Samples

These schemas and samples are critical for the implementation of the transformation and validation logic. They will be used as the basis for creating the `columns_mapping.json`, `fixed_columns.json`, and `descriptive_data.json` files, which will be consumed by the application.

### Column Mapping (`columns_mapping.json`)
This JSON object maps the Polish column names from the source Excel file to the English field names in the PostgreSQL database.

```json
{
  "Typ identyfikatora": "id_type",
  "Identyfikator": "id_value",
  "Produkt": "product_type",
  "Aktywny": "is_active",
  "Data obowiązywania od": "data_od",
  "Data obowiązywania do": "data_do"
}
```

### Fixed Columns Schema (`fixed_columns.json`)
This schema defines the required data types for the core columns that will be directly mapped to the database.

```json
{
  "id_type": "VARCHAR(255)",
  "id_value": "VARCHAR(255)",
  "product_type": "VARCHAR(255)",
  "login": "VARCHAR(255)",
  "data_od": "DATETIME",
  "data_do": "DATETIME",
  "dane_opisowe": "jsonb",
  "version": "TIMESTAMP"
}
```

### Descriptive Columns Schema (`descriptive_data.json`)
This schema defines the allowed data types for the dynamic, descriptive columns. Any column from the source Excel file not present in the `columns_mapping.json` will be validated against this schema. In Phase 1, this will be a local file. In Phase 2, this schema will be fetched from a REST API.

```json
{
  "taxi": "boolean",
  "czy włoski": "boolean",
  "prius": "boolean",
  "Prawdopodobieństwo zalania": "float",
  "Notatka": "string",
  "Ostatnia wizyta": "date"
}
```

### Sample Input Data
This table represents the structure and content of a typical source Excel file.

| Typ identyfikatora | Identyfikator       | Produkt | Aktywny | Data obowiązywania od | Data obowiązywania do | taxi | czy włoski | prius | Prawdopodobieństwo zalania | Notatka | Ostatnia wizyta |
|--------------------|---------------------|---------|---------|------------------------|------------------------|------|------------|--------|-----------------------------|---------|------------------|
| VIN                | WWWZZZ3BZ4E076409   | AUTO    | tak     | 2024-07-01             | 2025-07-01             | nie  | nie        | nie    |                             |         |                  |
| VIN                | WWWZZZ3BZ4E076408   | AUTO    | tak     | 2024-07-01             | 2025-07-01             | nie  | tak        | tak    |                             |         |                  |
| NR_DZIAŁKI         | 146518_8.0103.31/2  | ROLNE   | nie     | 2024-07-01             | 2025-07-01             |      |            |        | 123                         |         |                  |
| NR_DZIAŁKI         | 146503_8.0109.61    | DOM     | tak     | 2024-07-01             | 2025-07-01             |      |            |        |                             |         |                  |
| NR_REJ             | WA12345             | AUTO    | tak     | 2024-07-01             | 2025-07-01             | tak  | tak        | tak    |                             |         |                  |
| PESEL              | 78030714992         | AUTO    | tak     | 2024-07-01             | 2025-07-01             |      |            |        |                             |         | 2025-07-01       |
| PESEL              | 6231287548          | DOM     | tak     | 2024-07-01             | 2025-07-01             |      |            |        |                             |         |                  |
| PESEL              | 69071351178         | ROLNE   | tak     | 2024-07-01             | 2025-07-01             |      |            |        |                             |         |                  |
| VIN                | WWWZZZ3BZ4E076409   | AUTO    | tak     | 2024-07-01             | 2025-07-01             | tak  | tak        | tak    |                             |         |                  |
| PESEL              | 52030478900         |         | tak     | 2024-08-01             | 2025-08-01             |      |            |        |                             | brak    | 2025-04-15       |

### Sample Transformed Records
This shows how the raw data from the Excel file will be transformed into JSON objects before being loaded into the database. Note how the descriptive columns are grouped into the `dane_opisowe` field and how the empty `Produkt` for the last record is filled with `"all"`.

**VIN (Product = AUTO)**
```json
{
  "id_type": "VIN",
  "id_value": "WWWZZZ3BZ4E076409",
  "product_type": "AUTO",
  "is_active": "tak",
  "data_od": "2024-07-01",
  "data_do": "2025-07-01",
  "dane_opisowe": {
    "taxi": "nie",
    "czy włoski": "tak",
    "prius": "tak"
  }
}
```

**NR_DZIAŁKI (Product = ROLNE)**
```json
{
  "id_type": "NR_DZIAŁKI",
  "id_value": "146518_8.0103.31/2",
  "product_type": "ROLNE",
  "is_active": "nie",
  "data_od": "2024-07-01",
  "data_do": "2025-07-01",
  "dane_opisowe": {
    "Prawdopodobieństwo zalania": "123"
  }
}
```

**PESEL (Produkt = null → all)**
```json
{
  "id_type": "PESEL",
  "id_value": "52030478900",
  "product_type": "all",
  "is_active": "tak",
  "data_od": "2024-08-01",
  "data_do": "2025-08-01",
  "dane_opisowe": {
    "Notatka": "brak",
    "Ostatnia wizyta": "2025-04-15"
  }
}
``` 