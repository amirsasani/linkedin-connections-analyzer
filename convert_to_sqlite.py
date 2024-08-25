import sqlite3
import csv
import helper
import os

csv_file = 'data/linkedin_data.csv'
delimiter =';'

db_file = helper.getDatabaseFilePath()

db = sqlite3.connect(db_file)
cursor = db.cursor()

# Create a table with Id(AI), First Name, Last Name, URL, Company, Position, Connection Status, Location, Image columns
cursor.execute('''
    CREATE TABLE linkedin_data(
        Id INTEGER PRIMARY KEY AUTOINCREMENT,
        FirstName TEXT,
        LastName TEXT,
        URL TEXT,
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
    connection_status = row['Connection Status']
    location = ""
    image = ""

    if url == "" or url is None:
        return None  # Skip rows without a valid URL
    
    return (first_name, last_name, url, company, position, connection_status, location, image) 

# Read CSV file and insert data into the table
with open(csv_file, 'r', encoding='utf-8') as fin:
    dr = csv.DictReader(fin, delimiter=delimiter)

    print("Fieldnames detected:", dr.fieldnames)

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
                        ConnectionStatus = excluded.ConnectionStatus,
                        Location = excluded.Location,
                        Image = excluded.Image;
                ''', data)
                db.commit()
        except Exception as e:
            print(f"Error processing row {row}: {e}")

# Close resources
db.close()