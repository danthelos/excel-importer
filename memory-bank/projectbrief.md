# Project Brief: Excel Data Importer

## Overview
This project involves creating a Python application to automatically import data from Excel files in a SharePoint library into a PostgreSQL database. The application will handle data validation, transformation, logging, and error notifications. It will be developed in two phases, with the final version operating as an Airflow DAG.

## Core Requirements

### Phase 1
- **Configuration**: Store all credentials and endpoints in a `config.yaml` file.
- **Application Structure**: A main script will load the configuration and call helper functions from a `utils.py` file, which contains all the core logic.
- **SharePoint Integration**: Monitor a SharePoint library for new Excel files and retrieve the uploader's AD login.
- **Data Processing**:
    - Read data from fixed columns and dynamic descriptive columns.
    - Store descriptive data in a single `jsonb` column named `dane_opisowe`.
- **Data Validation & Transformation**:
    - Fill empty `Product` columns with `"all"`.
    - Verify that all required fixed columns are present.
    - Validate descriptive columns against a schema; ignore unlisted columns and check data types for listed ones.
- **Error Handling**:
    - On validation failure, send an email to the file owner and move the file to a `broken` folder in SharePoint.
- **Database Operations**:
    - If a record with the same `id_type`, `id_value`, and `product` exists, create a new version with a merged `dane_opisowe` and a new timestamp, leaving the old record untouched.
    - On success, save the new record to the database and move the file to an `imported` folder.
- **Logging**: Log all process events in a JSON format compatible with ElasticSearch.

### Phase 2
- **Airflow Integration**: Convert the application into an Airflow DAG for scheduled execution.
- **API-based Validation**: Fetch the validation schema for descriptive data from a REST API instead of a local file.

## Goals
- Automate the import of blacklist data from Excel files.
- Ensure high data quality through robust validation and error handling.
- Create a scalable and maintainable data pipeline using Airflow.
- Provide clear visibility into the import process through structured logging.

## Project Scope

### In Scope
- Building the Python application for data import (Phase 1).
- Converting the application into an Airflow DAG (Phase 2).
- Reading data from a SharePoint library.
- Connecting to and writing data to a PostgreSQL database.
- Implementing all data transformation, validation, and versioning logic as described.
- Sending email notifications for errors.
- Moving files within SharePoint to reflect their processing status (`imported`, `broken`).
- Structured JSON logging.

### Out of Scope
- The SharePoint library setup.
- The PostgreSQL database setup and administration.
- The Airflow environment setup.
- The REST API for schema validation (it is an external service to be consumed).
- A user interface for managing the process. 