import sqlite3 as sql3

# Step 1: Create a SQLite3 database file
db_file = "test_database.sqlite"  # Name of the database file
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

# Step 3: Insert sample data
sample_data = [
    ("Alice", "alice@example.com", "1234 Amie Blvd, San Antonio, Texas TX, USA"),
    ("Bob", "bob@example.com", "5678 Rua 5 de Julho, Sao Paulo, Sao Paulo SP, Brazil"),
    ("Charlie", "charlie@example.com", "806 Rua Nina Lopes, Rio de Janeiro RJ, Brazil")
]
cursor.executemany("INSERT INTO users (name, email, address) VALUES (?, ?, ?)", sample_data)
print("[INFO] Sample data inserted successfully.")

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

# Close the connection
test_database.close()
