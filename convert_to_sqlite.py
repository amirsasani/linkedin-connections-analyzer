import sqlite3
import csv
import helper

csv_file = 'data/linkedin_data.csv'
delimiter =','

db_file = helper.getDatabaseFilePath()

db = sqlite3.connect(db_file)
cursor = db.cursor()

# Create a table with Id(AI), First Name, Last Name, URL, Company, Position, Connection Status, Location, Image columns
cursor.execute('''
    CREATE TABLE IF NOT EXISTS linkedin_data (
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        FirstName TEXT,
        LastName TEXT,
        URL TEXT UNIQUE,
        Company TEXT,
        Position TEXT,
        ConnectionStatus TEXT,
        Location TEXT,
        Image TEXT
    )
''')

# Function to fetch user location and image
def process_row(row):
    first_name = row['First Name']
    last_name = row['Last Name']
    url = row['URL']
    company = row['Company']
    position = row['Position']
    connection_status = ""
    location = ""
    image = ""

    if url == "" or url is None:
        return None  # Skip rows without a valid URL
    
    return (first_name, last_name, url, company, position, connection_status, location, image) 

# Read CSV file and insert data into the table
# Open the file for reading
with open(csv_file, 'r', encoding='utf-8') as fin:
    header = None
    
    # Skip lines until you find the CSV header
    for line in fin:
        if "First Name,Last Name" in line:
            header = line
            break
    
    # Combine the header with the rest of the lines
    if header:
        remaining_lines = [header] + fin.readlines()
        dr = csv.DictReader(remaining_lines, delimiter=delimiter)

    print("Fieldnames detected:", dr.fieldnames)

    lines = 0

    for row in dr:
        try:
            data = process_row(row)
            if data:
                cursor.execute('''
                    INSERT INTO linkedin_data(
                        FirstName, LastName, URL, Company, Position, ConnectionStatus, Location, Image
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(URL) DO UPDATE SET
                        FirstName = excluded.FirstName,
                        LastName = excluded.LastName,
                        Company = excluded.Company,
                        Position = excluded.Position,
                        ConnectionStatus = CASE
                            WHEN excluded.ConnectionStatus != '' THEN excluded.ConnectionStatus
                            ELSE linkedin_data.ConnectionStatus
                        END,
                        Location = CASE
                            WHEN excluded.Location != '' THEN excluded.Location
                            ELSE linkedin_data.Location
                        END,
                        Image = CASE
                            WHEN excluded.Image != '' THEN excluded.Image
                            ELSE linkedin_data.Image
                        END;
                ''', data)
                db.commit()
                lines += 1
        except Exception as e:
            print(f"Error processing row {row}: {e}")

# Close resources
db.close()

print(f"Processed {lines} rows")