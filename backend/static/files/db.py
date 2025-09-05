import sqlite3

# Connect to SQLite database (or create it)
conn = sqlite3.connect("unimak.db")
cursor = conn.cursor()

# ------------------------
# Create tables
# ------------------------

# Users table
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    language TEXT DEFAULT 'en' 
)
""")

# Managers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS managers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_name TEXT NOT NULL UNIQUE
)
""")

# Engineers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS engineers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    engineer_name TEXT NOT NULL UNIQUE
)
""")

# Customers table
cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL UNIQUE,
    customer_country TEXT NOT NULL
)
""")

# Projects table
cursor.execute("""
CREATE TABLE IF NOT EXISTS projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_number TEXT NOT NULL UNIQUE,
    project_name TEXT NOT NULL UNIQUE,
    manager_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    FOREIGN KEY (manager_id) REFERENCES managers(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
)
""")

# Groups table
cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    engineer_id INTEGER NOT NULL,
    component_no TEXT NOT NULL,
    component_name TEXT NOT NULL,
    unit_quantity INTEGER NOT NULL,
    total_quantity INTEGER NOT NULL,
    weight FLOAT, -- can be null
    description TEXT, -- can be null
    size TEXT, -- can be null
    material TEXT NOT NULL,
    machine_type TEXT NOT NULL,
    notes TEXT, -- can be null
    working_area TEXT NOT NULL,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (engineer_id) REFERENCES engineers(id)
)
""")

# Problems table
cursor.execute("""
CREATE TABLE IF NOT EXISTS problems (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    df_number TEXT UNIQUE NOT NULL,       -- latest df report
    recorder_id INTEGER NOT NULL,
    reason TEXT NOT NULL,
    description TEXT,
    photos_id TEXT,
    status TEXT DEFAULT 'waiting',        -- 11 different statuses possible
    record_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (recorder_id) REFERENCES users(id)
)
""")

# Problem steps table (history)
cursor.execute("""
CREATE TABLE IF NOT EXISTS problem_steps (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    problem_id INTEGER NOT NULL,
    step_number INTEGER NOT NULL,
    df_filename TEXT NOT NULL,           -- e.g., df_1.xlsx, df_2.xlsx
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (problem_id) REFERENCES problems(id)
)
""")

# ------------------------
# Commit and close
# ------------------------
conn.commit()
conn.close()

print("Database 'unimak.db' created successfully with problem steps workflow!")
