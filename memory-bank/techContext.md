# Tech Context: Excel Data Importer

## Technologies Used
- **Programming Language**: Python 3.x
- **Data Storage**: PostgreSQL (for blacklist data), SharePoint (for Excel files)
- **Orchestration**:
  - **Phase 1**: System scheduler (e.g., cron)
  - **Phase 2**: Apache Airflow
- **Key Python Libraries**:
  - `pandas` / `openpyxl`: For reading Excel files.
  - `psycopg2-binary`: For PostgreSQL interaction.
  - `PyYAML`: For parsing the configuration file.
  - `Office365-REST-Python-Client` (or similar): For SharePoint API communication.
  - `requests`: For Phase 2 REST API calls.
  - `logging`: For structured JSON logging.
- **Configuration Format**: YAML
- **Data Interchange Format**: JSON (for `dane_opisowe` and logs)

## Development Setup
1.  **Environment**: Create and activate a Python virtual environment (e.g., `python -m venv .venv`).
2.  **Dependencies**: Install all required packages using `pip install -r requirements.txt`.
3.  **Configuration**:
    - Create a `config.yaml` file from a provided template.
    - Populate it with valid credentials and URLs for your development SharePoint site and PostgreSQL database. **Do not commit this file.**
4.  **Database Schema**: Ensure the `blacklist.entity` table exists in the PostgreSQL database with the correct schema (`id_type`, `id_value`, `product`, `dane_opisowe`, etc.).
5.  **SharePoint Folders**: Create the necessary folders in the SharePoint library: a root folder to monitor, and sub-folders named `imported` and `broken`.
6.  **Airflow (Phase 2)**: A local Airflow instance (e.g., via the official Docker Compose setup) will be required for developing and testing the DAG.

## Technical Constraints
- **Network Access**: The application's runtime environment must have network access to both the SharePoint Online service and the PostgreSQL database host.
- **External API Dependency (Phase 2)**: The system's ability to validate descriptive data in Phase 2 is entirely dependent on the availability and correctness of the external schema REST API.
- **Statelessness**: The application itself must be stateless. All state is maintained externally in SharePoint (by moving files) and in the PostgreSQL database (by storing records). This is crucial for running in a distributed environment like Airflow.

## Dependencies
- **SharePoint Client Library**: A specific Python library to handle authentication and interaction with the SharePoint REST API. The exact choice will be a key decision.
- **PostgreSQL Driver**: `psycopg2` is the standard, but alternatives could be considered if performance issues arise.
- **Airflow Environment (Phase 2)**: A functional Airflow deployment is required to run the final version of the pipeline.

## Tool Usage Patterns
- **Version Control**: Git should be used for all code changes. A feature-branch workflow is recommended.
- **Dependency Management**: All Python dependencies must be explicitly listed with their versions in a `requirements.txt` file to ensure reproducible builds.
- **Configuration**: All environment-specific variables, credentials, and endpoints **must** be managed in the `config.yaml` file. There should be no hardcoded secrets in the source code.
- **Logging**: The standard `logging` library should be configured at the start of the application to output structured JSON. This ensures that logs are machine-readable and can be easily ingested by services like ElasticSearch.
- **Test Utils**: `test_utils.py` is used for generating mock data for local testing.

## Data Schemas and Samples

These schemas and samples are critical for the implementation of the transformation and validation logic. They will be used as the basis for creating the `columns_mapping.json`, `fixed_columns.json`, and `descriptive_data.json` files, which will be consumed by the application.

### Column Mapping (`columns_mapping.json`)
This JSON object maps the Polish column names from the source Excel file to the English field names in the PostgreSQL database.

```json
{
  "Typ identyfikatora": "id_type",
  "Identyfikator": "id_value",
  "Produkt": "product",
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
  "product": "VARCHAR(255)",
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
  "product": "AUTO",
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
  "product": "ROLNE",
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
  "product": "all",
  "is_active": "tak",
  "data_od": "2024-08-01",
  "data_do": "2025-08-01",
  "dane_opisowe": {
    "Notatka": "brak",
    "Ostatnia wizyta": "2025-04-15"
  }
}
``` 