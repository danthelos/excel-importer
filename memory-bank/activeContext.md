# Active Context: Excel Data Importer

## Current Work Focus
The project is moving from core logic implementation to integration. The immediate focus is on replacing the placeholder functions in `utils.py` with code that connects to and interacts with live external services (SharePoint, PostgreSQL, SMTP).

## Recent Changes
- **Code Refactoring**: The project has been refactored to completely separate test execution (`run_tests.py`) from the production application (`main.py`).
- **Negative Testing Implemented**: The test framework has been enhanced to validate against known-bad data in `test_data.xlsx`, and the test runner now asserts that specific errors are caught.
- **Successful Test Run**: The dedicated test script has been successfully run, correctly identifying all expected errors in the test data.
- **Application Skeleton**: The production entry point, `main.py`, is now a clean skeleton ready for live integration.
- **Pandas Best Practices**: Addressed a `FutureWarning` in pandas to ensure forward compatibility.

## Next Steps
1.  **Implement SharePoint Integration**:
    -   Replace the `get_new_files` and `move_file` placeholder functions in `utils.py` with live code using the `Office365-REST-Python-Client` library.
    -   Verify that the file author's login can be retrieved.
2.  **Implement Database Integration**:
    -   Replace the `connect_to_db` and `insert_record` functions with live code using the `psycopg2` library.
3.  **Implement Email Notifications**:
    -   Replace the `send_error_email` function with live code using Python's `smtplib`.

## Active Decisions and Considerations
- **Credential Management**: As we move to live integrations, ensuring that credentials in `config.yaml` are handled securely and are not committed to version control is paramount. The `.gitignore` file should be updated to include `config.yaml`.
- **SharePoint API**: The specific API calls needed to fetch the file author's email and move files efficiently need to be confirmed during implementation.
- **Error Handling**: The real implementation of placeholder functions must include robust error handling for scenarios like failed connections, permissions issues, or API errors.

## Important Patterns and Preferences
- **Modularity**: Continue to ensure that all functions in `utils.py` are self-contained and have a single responsibility.
- **Type Hinting**: Maintain strict type hinting for all new code.
- **Defensive Coding**: All new code that interacts with external systems must be wrapped in `try...except` blocks.

## Learnings and Project Insights
- A robust testing strategy must include negative test cases to ensure that data validation logic is working as expected. Asserting that specific errors are caught is more reliable than simply checking if a process fails.
- Separating test execution (`run_tests.py`) from application code (`main.py`) provides a much cleaner project structure and a more realistic development workflow.
- Using a physical test file (`test_data.xlsx`) for local runs provides higher fidelity testing and ensures the Excel parsing logic itself is validated, not just the subsequent transformations.
- Iterative testing is crucial for identifying issues (like the pandas `FutureWarning`) early in the development process. 