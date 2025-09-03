import pandas as pd
import sqlite3

# 1️⃣ Load Excel data
df = pd.read_excel(
    "/home/gokhan/UNIMAK/info/demo/25016_140000 - NOZUL-ENJEKTOR-VALF GRUBU.xlsx",
    usecols="A:L",
    skiprows=6,
    nrows=77
)

# Optional: rename columns to match your SQL table
df.columns = [
    "position_no", "component_no", "component_name", "unit_quantity", "total_quantity",
    "weight", "description", "size", "materials", "machine_type", "notes", "working_area"
]

# 2️⃣ Connect to SQLite
conn = sqlite3.connect("unimak.db")
cursor = conn.cursor()

# 3️⃣ Insert rows into the database
group_id = 4  # set your group_id here

for index, row in df.iterrows():
    cursor.execute("""
        INSERT INTO components (
            group_id, position_no, component_no, component_name, unit_quantity, total_quantity,
            weight, description, size, materials, machine_type, notes, working_area
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        group_id,
        row['position_no'], row['component_no'], row['component_name'],
        row['unit_quantity'], row['total_quantity'], row['weight'],
        row['description'], row['size'], row['materials'], row['machine_type'],
        row['notes'], row['working_area']
    ))

# 4️⃣ Commit and close
conn.commit()
conn.close()
print(df)