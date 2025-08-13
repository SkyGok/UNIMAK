import sqlite3

# Create or connect to the SQLite database
conn = sqlite3.connect("unimak.db")
cursor = conn.cursor()

# Create users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

# Create finances table
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    project_number TEXT NOT NULL,
    project_manager TEXT NOT NULL,
    reason TEXT,
    description TEXT,
    folder_name TEXT NOT NULL,
    record_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)

""")

# Commit changes and close connection
conn.commit()
conn.close()

print("Database and tables created successfully.")
