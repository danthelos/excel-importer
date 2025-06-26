# Excel Data Importer

## Opis aplikacji

This project involves creating a Python application to automatically import data from Excel files and process them through several development phases, starting with local file operations and culminating in full enterprise integration with SharePoint Server 2019 and Airflow. - Read Excel files from a local folder. - Validate and transform the data as per business rules. - Export the processed data to a CSV file in a local folder. - **Log all process events in JSON format compatible with ElasticSearch after successful CSV export (Phase 1).** - In Phase 1, all good rows from all Excel files in the input folder are appended to a single output CSV file (`output/data.csv`). This simulates a database table and supports versioning/merging logic across files. There are no per-file CSV exports. - If a record (combination of `id_type`, `id_value`, `product_type`) already exists in the output CSV: - Retrieve the `dane_opisowe` column from the old record - Create a new record with an updated `version` (timestamp) - Merge the old and new descriptive data (new values overwrite old keys) - Leave the old record unchanged (append the new version as a new row) - All data directories (input, output, imported, broken) are under `/data` and are configurable in `config.yaml`.

---

## Dla użytkownika

- **Cel**: Automatyczny import danych z plików Excel do bazy danych.
- **Jak używać**:
  1. Skonfiguruj plik `config.yaml` (ścieżki, dane logowania, itp.).
  2. Umieść pliki Excel w odpowiednim folderze lub bibliotece SharePoint.
  3. Uruchom aplikację:  
     ```bash
     python main.py
     ```
  4. Przetworzone pliki trafią do folderu `imported` lub `broken` (w zależności od wyniku walidacji).

- **Wymagania**:
  - Python 3.8+
  - PostgreSQL
  - (opcjonalnie) SharePoint Server 2019

Więcej informacji: [Szczegółowy opis projektu](memory-bank/projectbrief.md)

---

## Dla developera

- **Architektura i fazy rozwoju**:  
  Szczegóły znajdziesz w [projectbrief.md](memory-bank/projectbrief.md) oraz [progress.md](memory-bank/progress.md).
- **Aktualny stan projektu**:  
  [Zobacz aktywny kontekst](memory-bank/activeContext.md)
- **Roadmapa i postępy**:  
  [Zobacz postępy](memory-bank/progress.md)
- **Wzorce i decyzje systemowe**:  
  [System Patterns](memory-bank/systemPatterns.md)
- **Kontekst techniczny**:  
  [Tech Context](memory-bank/techContext.md)

---

## Dokumentacja Memory Bank

- [Projectbrief](memory-bank/projectbrief.md)
- [Activecontext](memory-bank/activeContext.md)
- [Progress](memory-bank/progress.md)
- [Systempatterns](memory-bank/systemPatterns.md)
- [Techcontext](memory-bank/techContext.md)
- [Productcontext](memory-bank/productContext.md)
- [Memory Bank Instructions](memory-bank/memory_bank_instructions.md)

---

## Licencja

MIT
