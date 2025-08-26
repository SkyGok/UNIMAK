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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    language TEXT DEFAULT 'en' 
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS managers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_name TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL UNIQUE,
    customer_country TEXT NOT NULL UNIQUE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_number TEXT NOT NULL UNIQUE,
    manager_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    machine_type TEXT NOT NULL UNIQUE,
    machine_top_group TEXT NOT NULL UNIQUE,
    FOREIGN KEY (manager_id) REFERENCES managers(id)
)
""")

cursor.execute("""
CREATE TABLE problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_number INTEGER NOT NULL,        -- foreign key to projects.id
    df_number TEXT UNIQUE NOT NULL,         -- e.g., df_220820251659
    reason TEXT NOT NULL,
    description TEXT,
    photos_id TEXT,                         -- store photo filenames or IDs
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(project_number) REFERENCES projects(id)
)
""")

# Commit changes and close connection
conn.commit()
conn.close()

print("Database and tables created successfully.")
