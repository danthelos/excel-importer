# Active Context: Excel Data Importer

## Current Work Focus
Phase 3 is now implemented. The application can fetch Excel files directly from a SharePoint Server 2019 document library, process and validate them, export good data to the PostgreSQL database, and move files to 'imported' or 'broken' folders in SharePoint. If SharePoint config is not present, the app falls back to local folder processing. All steps are logged in structured JSON format. The next step is to test SharePoint integration in a real environment and refine error handling and user notification as needed.

## Recent Changes
- **SharePoint Integration**: Added logic to fetch, process, and move Excel files from SharePoint Server 2019. Uses `Office365-REST-Python-Client` for on-premises SharePoint.
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