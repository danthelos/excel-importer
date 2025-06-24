## 🧩 Task Description – Importing Excel Data from SharePoint to PostgreSQL

### 🎯 Objective
Create a Python application that automatically imports data from Excel files placed in a SharePoint library and stores them in the `blacklist.entity` table in a PostgreSQL database. The mechanism will be integrated into an Airflow DAG and will support data validation, event logging, and error handling.

---

### 🛠️ Technical Requirements – Phase 1

- Store configuration in a `config.yaml` file, including:
  - `sharepoint_user_login`
  - `sharepoint_user_password`
  - `sharepoint_library_url`
  - `db_user_login`
  - `db_user_password`
  - `db_host`
  - `db_port`
  - `db_name`

- Application structure:
  - The main script loads variables from YAML and uses helper functions from `utils.py`.
  - All functionality (import logic, validation, saving) should be implemented in `utils.py`.

- Application behavior:
  - Monitor the SharePoint library and detect newly added Excel files.
  - Retrieve the AD login of the user who uploaded the file (file metadata).
  - Read data from two areas:
    - **Fixed columns** (from `Identifier Type` to `Valid To`)
    - **Descriptive data** – all remaining columns are stored as a single `jsonb` column called `dane_opisowe`
  - Before saving:
    - If the `Product` column is empty, fill it with `"all"`
    - Verify that all required fixed columns are present in the Excel file
    - Validate descriptive columns using the schema file:
      - If a column is not listed in the dictionary – ignore it
      - If it is listed – verify its data type
  - On validation error:
    - Send an email to the file owner (`login`)
    - Move the file to the `broken` folder on SharePoint
  - If a record (combination of `id_type`, `id_value`, `product_type`) already exists:
    - Retrieve the `dane_opisowe` column from the old record
    - Create a new record with an updated `version` (timestamp)
    - Merge the old and new descriptive data
    - Leave the old record unchanged
  - On success:
    - Save the new record to the database
    - Move the file to the `imported` folder

- The `version` column should be populated with the current timestamp.
- Process events should be logged in JSON format compatible with ElasticSearch, including: `timestamp`, `level`, `action`, `result`.

---

### 🔁 Technical Requirements – Phase 2

- Convert the mechanism into an **Airflow DAG**.
- Descriptive data validation (`dane_opisowe`) should be performed using a REST API instead of a local file. This requires:
  - Adding `schema_api_user`, `schema_api_password`, and `schema_api_url` to the YAML config file
  - Updating the validation logic to fetch the schema from the API

---

### 📌 Column Mapping from Excel to Database

A `columns_mapping.json` file is required to map Excel headers to target database fields:

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

All other columns not included in this mapping will be serialized into a JSON structure and stored under the dane_opisowe field.

### Auxiliary Schemas

#### fixed_columns.json:  

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

#### descriptive_data.json:  

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

#### Sample table to import:

| Identifier Type | Identifier       | Product | Active | Valid From | Valid To | taxi | czy włoski | prius | Prawdopodobieństwo zalania | Note | Last Visit |
|--------------------|---------------------|---------|---------|------------------------|------------------------|------|------------|--------|-----------------------------|---------|------------------|
| VIN                | WWWZZZ3BZ4E076409   | AUTO    | yes     | 2024-07-01             | 2025-07-01             | no   | no         | no     |                             |         |                  |
| VIN                | WWWZZZ3BZ4E076408   | AUTO    | yes     | 2024-07-01             | 2025-07-01             | no   | yes        | yes    |                             |         |                  |
| NR_DZIAŁKI         | 146518_8.0103.31/2  | ROLNE   | no      | 2024-07-01             | 2025-07-01             |      |            |        | 123                         |         |                  |
| NR_DZIAŁKI         | 146503_8.0109.61    | DOM     | yes     | 2024-07-01             | 2025-07-01             |      |            |        |                             |         |                  |
| NR_REJ             | WA12345             | AUTO    | yes     | 2024-07-01             | 2025-07-01             | yes  | yes        | yes    |                             |         |                  |
| PESEL              | 78030714992         | AUTO    | yes     | 2024-07-01             | 2025-07-01             |  |         |     |                             |     | 2025-07-01       |
| PESEL              | 6231287548          | DOM     | yes     | 2024-07-01             | 2025-07-01             |   |         |     |                             |      |                  |
| PESEL              | 69071351178         | ROLNE   | yes     | 2024-07-01             | 2025-07-01             |   |        |     |                             |         |                  |
| VIN                | WWWZZZ3BZ4E076409   | AUTO    | yes     | 2024-07-01             | 2025-07-01             | yes  | yes        | yes    |                             |         |                  |
| PESEL              | 52030478900         |         | yes     | 2024-08-01             | 2025-08-01             |   |         |     |                        | none     | 2025-04-15       |

#### Sample Transformed Records
VIN (Product = AUTO)

```json
{
  "id_type": "VIN",
  "id_value": "WWWZZZ3BZ4E076409",
  "product_type": "AUTO",
  "is_active": "yes",
  "data_od": "2024-07-01",
  "data_do": "2025-07-01",
  "dane_opisowe": {
    "taxi": "no",
    "czy włoski": "yes",
    "prius": "yes"
  }
}
```

NR_DZIAŁKI (Produkt = ROLNE)

```json
{
  "id_type": "NR_DZIAŁKI",
  "id_value": "146518_8.0103.31/2",
  "product_type": "ROLNE",
  "is_active": "no",
  "data_od": "2024-07-01",
  "data_do": "2025-07-01",
  "dane_opisowe": {
    "Prawdopodobieństwo zalania": "123"
  }
}
```

PESEL (Produkt = null → all)

```json
{
  "id_type": "PESEL",
  "id_value": "52030478900",
  "product_type": "all",
  "is_active": "yes",
  "data_od": "2024-08-01",
  "data_do": "2025-08-01",
  "dane_opisowe": {
    "Note": "none",
    "Last Visit": "2025-04-15"
  }
}
```