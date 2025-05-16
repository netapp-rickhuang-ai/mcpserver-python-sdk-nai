import logging
import sqlite3 as sql3

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)
logger.info("\n[INFO] Starting connection to SQLite3 server for creating text table.")

# Step 1: Create a SQLite3 database file
db_file = "text_database.sqlite"  # Name of the database file
connection = sql3.connect(db_file)  # Create or connect to the database
cursor = connection.cursor()

# Step 2: Define a schema and create a table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    address TEXT NOT NULL
)
""")
print("[INFO] Table 'users' created successfully.")

cursor.execute("""
CREATE TABLE IF NOT EXISTS text (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL
)
""")
print("[INFO] Table 'text' created successfully.")
logger.info("[INFO] Table 'text' created successfully.")

# Step 3: Insert sample data
# sample_data = [
#     ("Alice", "alice@example.com", "1234 Amie Blvd, San Antonio, Texas TX, USA"),
#     ("Bob", "bob@example.com", "5678 Rua 5 de Julho, Sao Paulo, Sao Paulo SP, Brazil"),
#     ("Charlie", "charlie@example.com", "806 Rua Nina Lopes, Rio de Janeiro RJ, Brazil")
# ]
sample_data = [
    ("Allen Walker", "allen.walker@example.com", "12345 Amie Blvd, San Antonio, Texas TX, USA"),
    ("Bobby Fisher", "bobby.fisher@example.com", "5678 Rua 5 de Julho, Sao Paulo, Sao Paulo SP, Brazil"),
    ("Charles James", "charles.james@example.com", "806 Rochester Lane, London, United Kingdom")
]
sample_txt_data = "This is some sample text."
    # ("This is another sample text.")

cursor.executemany("INSERT INTO users (name, email, address) VALUES (?, ?, ?)", sample_data)
cursor.execute("INSERT INTO text (content) VALUES (?)", (sample_txt_data,))
print("[INFO] Sample data inserted successfully into TABLEs users, text.")

# Step 4: Commit changes and close the connection
connection.commit()
connection.close()
print(f"[INFO] Database saved as '{db_file}'.")

# Step 5: Use the saved database as `test_database`
# from fake_database import Database  # Replace with your actual DB type

# Example usage of the saved database
test_database = sql3.connect(db_file)  # Connect to the saved SQLite3 database
cursor = test_database.cursor()

# Query the database
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()
print("[INFO] Users in the database:")
for row in rows:
    print(row)

cursor.execute("SELECT * FROM text")
txt_rows = cursor.fetchall()
print("[INFO] Text table in the database:")
for row in txt_rows:
    print(row)

# Close the connection
test_database.close()
