import sqlite3

# Connect to the SQLite database (or create it if it doesn't exist)
connection = sqlite3.connect('certifications_data.db')
cursor = connection.cursor()

# Create the table 'certifications_data' with 'certification_name' and 'points' columns
cursor.execute('''
     CREATE TABLE IF NOT EXISTS certifications_table (
        cert_name TEXT NOT NULL,
        points INTEGER
    )
''')

# Insert 3-4 rows into the table
certificate_data = [
    ('Any Professional or Specialty', 10),
    ('Any Associate or Hashicorp', 5),
    ('Anything Else', 2.5)
]

cursor.executemany("INSERT INTO certifications_table VALUES (?, ?)", certificate_data)

# Commit the changes and close the connection
connection.commit()
connection.close()

print("Table 'certifications_table' created inside 'certification_data.db'and data inserted successfully!")