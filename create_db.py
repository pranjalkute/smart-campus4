import sqlite3

conn = sqlite3.connect("database.db")

conn.execute("""
CREATE TABLE IF NOT EXISTS complaints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    issue TEXT,
    description TEXT,
    category TEXT,
    confidence INTEGER,
    image TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully")