import pandas as pd
import numpy as np

def create_test_excel_file():
    """
    Creates an Excel file with a mix of valid and invalid sample data for testing.
    """
    sample_data = {
        'Typ identyfikatora':     ['PESEL', 'VIN', np.nan, 'REGON', 'NIP', 'PESEL'],
        'Identyfikator':          ['52030478900', 'WWWZZZ3BZ4E076409', '12345', '123456785', '1234567890', '9876543210'],
        'Produkt':                [None, 'AUTO', 'DOM', 'ROLNE', 'AUTO', 'DOM'],
        'Aktywny':                ['tak', 'tak', 'tak', 'tak', 'tak', 'tak'],
        'Data obowiązywania od': ['2024-08-01', '2024-07-01', '2024-01-01', 'not a date', '2024-01-01', '2024-01-01'],
        'Data obowiązywania do': ['2025-08-01', '2025-07-01', '2025-01-01', '2025-01-01', '2025-01-01', '2025-01-01'],
        'Notatka':                ['brak', None, None, None, None, None],
        'Ostatnia wizyta':        ['2025-04-15', None, None, None, None, None],
        'taxi':                   [None, 'tak', None, None, None, "some string"], # Invalid boolean
        'czy włoski':             [None, 'nie', None, None, None, None],
        'prius':                  [None, 'tak', None, None, None, None],
        'not known key':          [None, None, None, None, 'string value', None] # Should be ignored
    }
    df = pd.DataFrame(sample_data)
    
    output_filename = 'test_data.xlsx'
    df.to_excel(output_filename, index=False)
    print(f"Successfully created '{output_filename}' with valid and invalid data.")

if __name__ == "__main__":
    create_test_excel_file() 