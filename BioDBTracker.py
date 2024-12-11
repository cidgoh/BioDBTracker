import os
import yaml
import sqlite3
import argparse
import gspread
from oauth2client.service_account import ServiceAccountCredentials

def parse_arguments():
    parser = argparse.ArgumentParser(description='Scan directories and update the SQL database with version information.')
    parser.add_argument(
        '-i', '--input', 
        type=str, 
        nargs='+',  # Allow multiple folder paths
        required=True, 
        help='The base path(s) to start scanning from. Provide one or more folder paths separated by space.'
    )
    parser.add_argument(
        '-db', '--database', 
        type=str, 
        default=os.path.join(os.getcwd(), 'database_info.db'),  # Default to current folder
        help='The location of the database_info.db file. Defaults to the current directory.'
    )
    parser.add_argument(
        '-gs', '--google_sheet', 
        action='store_true',  # Toggle for uploading to Google Sheets
        help='If provided, data will be uploaded to Google Sheets. Requires additional parameters.'
    )
    parser.add_argument(
        '-gsn', '--google_sheet_name', 
        type=str, 
        help='The name of the Google Sheet to upload data to. Required if --google_sheet is specified.'
    )
    parser.add_argument(
        '-gss', '--google_sheet_sheet', 
        type=str, 
        help='The name of the worksheet in the Google Sheet. Required if --google_sheet is specified.'
    )
    parser.add_argument(
        '-gsc', '--google_credentials', 
        type=str, 
        help='Path to the Google API credentials JSON file. Required if --google_sheet is specified.'
    )
    return parser.parse_args()

def scan_directories(base_path):
    data = []
    for root, dirs, files in os.walk(base_path):
        if 'version.yml' in files:
            version_file_path = os.path.join(root, 'version.yml')
            database_path = os.path.abspath(root)

            with open(version_file_path, 'r') as file:
                version_info = yaml.safe_load(file)

                data.append({
                    'database_path': database_path,
                    'info': version_info.get('database_info', {})  # Use .get() to avoid KeyError
                })
    print(data)             
    return data

def write_to_sql(data, database_path):
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS DatabaseInfo (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            version TEXT,
            database_path TEXT,
            date TEXT,
            downloaded_from TEXT,
            downloaded_by TEXT,
            tested_by TEXT,
            note TEXT,
            UNIQUE(name, version)
        )
    ''')

    for entry in data:
        db_path = entry['database_path']
        info = entry['info']
        name = info.get('name', '')
        version = info.get('version', '')

        # Check if the entry already exists
        cursor.execute('''
            SELECT * FROM DatabaseInfo WHERE name = ? AND version = ?
        ''', (name, version))
        
        if cursor.fetchone():
            # Update existing record
            cursor.execute('''
                UPDATE DatabaseInfo
                SET date = ?, downloaded_from = ?, downloaded_by = ?, tested_by = ?, database_path = ?, note = ? 
                WHERE name = ? AND version = ?
            ''', (
                info.get('date', ''),
                info.get('downloaded_from', ''),
                info.get('downloaded_by', ''),
                info.get('tested_by', ''),
                db_path, 
                info.get('note', ''), 
                info.get('name', ''),
                info.get('version', '')
            ))
        else:
            # Insert new record
            cursor.execute('''
                INSERT INTO DatabaseInfo (
                    name, version, database_path, date, downloaded_from, downloaded_by, tested_by, note
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                info.get('name', ''),
                info.get('version', ''),
                db_path,
                info.get('date', ''),
                info.get('downloaded_from', ''),
                info.get('downloaded_by', ''),
                info.get('tested_by', ''),
                info.get('note', '')
            ))
    
    conn.commit()
    conn.close()

def write_to_google_sheets(data, google_sheet_name, google_sheet_sheet, google_credentials):
    # Define the scope and authenticate
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(google_credentials, scope)
    client = gspread.authorize(creds)

    # Open the Google Sheet
    try:
        spreadsheet = client.open(google_sheet_name)  # Use the provided Google Sheet name
        sheet = spreadsheet.worksheet(google_sheet_sheet)  # Use the provided worksheet name
    except gspread.SpreadsheetNotFound:
        print("Spreadsheet not found. Please check the name and permissions.")
        return
    except gspread.WorksheetNotFound:
        print(f"Worksheet '{google_sheet_sheet}' not found. Please check the name of the sheet.")
        return

   # Fetch all existing records from the Google Sheet
    existing_records = sheet.get_all_records()  # Returns a list of dictionaries
    existing_records_dict = {
        (row.get('Name', '').strip(), row.get('Version', '').strip()): {
            'Location': row.get('Location', '').strip(),
            'Date': row.get('Date', '').strip(),
            'Source': row.get('Source', '').strip(),
            'Downloaded_by': row.get('Downloaded_by', '').strip(),
            'Tested_by': row.get('Tested_by', '').strip(),
            'Note': row.get('Note', '').strip()
        }
        for row in existing_records if row.get('Name') and row.get('Version')  # Only include valid rows
    }

    # Map records to their row numbers for updating
    existing_row_indices = {
        (row.get('Name', '').strip(), row.get('Version', '').strip()): idx + 2  # Adjust for 1-based indexing and header
        for idx, row in enumerate(existing_records)
        if row.get('Name') and row.get('Version')
    }

    for entry in data:
        db_path = entry['database_path']
        info = entry['info']

        # Build the new row data
        new_row = {
            'Name': info.get('name', '').strip(),
            'Version': info.get('version', '').strip(),
            'Location': db_path.strip(),
            'Date': info.get('date', '').strip(),
            'Source': info.get('downloaded_from', '').strip(),
            'Downloaded_by': info.get('downloaded_by', '').strip(),
            'Tested_by': info.get('tested_by', '').strip(),
            'Note': info.get('note', '').strip(),
        }

        key = (new_row['Name'], new_row['Version'])

        if key in existing_records_dict:
            # Check if the existing record differs from the new one
            existing_record = existing_records_dict[key]
            if any(existing_record[field] != new_row[field] for field in new_row if field != 'Name' and field != 'Version'):
                # Update the row if any field (other than Name/Version) is different
                row_index = existing_row_indices[key]
                print(f"Updating row for {key} at index {row_index}")
                sheet.update(
                    values=[[new_row['Name'], new_row['Version'], new_row['Location'], new_row['Date'], new_row['Source'],
                             new_row['Downloaded_by'], new_row['Tested_by'], new_row['Note']]],
                    range_name=f"A{row_index}:H{row_index}"
                )
            else:
                print(f"Skipping unchanged row for {key}")
        else:
            # Add new record to the Google Sheet
            print(f"Adding new row for {key}")
            sheet.append_row([
                new_row['Name'],
                new_row['Version'],
                new_row['Location'],
                new_row['Date'],
                new_row['Source'],
                new_row['Downloaded_by'],
                new_row['Tested_by'],
                new_row['Note']
            ])

def main():
    args = parse_arguments()
    base_paths = args.input  # A list of folder paths
    database_path = args.database
    upload_to_google_sheets = args.google_sheet
    google_sheet_name = args.google_sheet_name
    google_sheet_sheet = args.google_sheet_sheet
    google_credentials = args.google_credentials

    # Validate Google Sheets parameters if enabled
    if upload_to_google_sheets:
        if not all([google_sheet_name, google_sheet_sheet, google_credentials]):
            print("Google Sheets upload requires --google_sheet_name, --google_sheet_sheet, and --google_credentials.")
            return

    version_data = []
    for base_path in base_paths:
        version_data.extend(scan_directories(base_path))
        
    write_to_sql(version_data, database_path)
    
    if upload_to_google_sheets:
        write_to_google_sheets(version_data, google_sheet_name, google_sheet_sheet, google_credentials)

if __name__ == "__main__":
    main()

