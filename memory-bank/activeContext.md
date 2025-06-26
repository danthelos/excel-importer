# Active Context: Excel Data Importer

## Current Work Focus
Phase 3 is now implemented. The application can fetch Excel files directly from a SharePoint Server 2019 document library, process and validate them, export good data to the PostgreSQL database, and move files to 'imported' or 'broken' folders in SharePoint. If SharePoint config is not present, the app falls back to local folder processing. All steps are logged in structured JSON format. The application now also fetches the author's email from SharePoint file metadata and uses it for error notification emails. The SharePoint configuration now uses explicit variables for source_folder, imported_folder, and broken_folder, and the code references these variables for all SharePoint operations. Email notification is fully implemented and operational. The next step is to test SharePoint integration in a real environment and refine error handling and user notification as needed.

## Email Notification Implementation (Complete)
- Email notification is fully implemented and operational.
- When an error occurs during file import (validation or processing), the application sends an email notification to the file's author.
- The recipient's email address is extracted from the SharePoint file metadata (Author.Email). If unavailable, a default sender address from config is used.
- The email contains a subject with a configurable prefix and a detailed error report in the body.
- All email content (recipient, subject, body) is always logged at INFO level, regardless of whether the email is actually sent or just logged (controlled by the config flag 'sending_email_enabled').
- Email sending is performed via SMTP without authentication, using server and sender details from the config file.
- All email notification settings are managed in the 'notifications' section of config.yaml.

## Recent Changes
- **SharePoint Integration**: Added logic to fetch, process, and move Excel files from SharePoint Server 2019. Uses `Office365-REST-Python-Client` for on-premises SharePoint.
- **Author Email Extraction**: The application now extracts the author's email from SharePoint file metadata and uses it as the recipient for error notification emails.
- **SharePoint Folder Variables**: The SharePoint configuration now uses explicit variables for source_folder, imported_folder, and broken_folder, and the code references these variables for all SharePoint operations.
- **Fallback Logic**: If SharePoint config is missing, the app uses the local folder workflow as before.
- **Unified Processing**: Both SharePoint and local files are processed with the same validation, transformation, and export logic.
- **Structured Logging**: All actions and errors are logged in JSON format for traceability.

## Next Steps
- Test SharePoint integration in a real environment.
- Refine error handling and notification for SharePoint workflows.
- Prepare for Phase 4: Airflow orchestration and schema API integration.

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