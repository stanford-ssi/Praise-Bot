# migrate_mysql_to_sqlite.py

import sqlite3
import mysql.connector
from pathlib import Path
from dotenv import load_dotenv
import os

# Load env vars for MySQL
load_dotenv(dotenv_path=Path('.') / '.env')

# Connect to MySQL
mysql_conn = mysql.connector.connect(
    host=os.environ['DB_HOST'],
    user=os.environ['DB_USER'],
    password=os.environ['DB_PASS'],
    database=os.environ['DB_DATABASE']
)
mysql_cursor = mysql_conn.cursor()

# Connect to SQLite
sqlite_conn = sqlite3.connect("Praise_Database.db")
sqlite_cursor = sqlite_conn.cursor()

# Create table in SQLite if it doesn't exist
sqlite_cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT,
        points INTEGER DEFAULT 0
    );
""")
sqlite_conn.commit()

# Fetch from MySQL
mysql_cursor.execute("SELECT id, name, points FROM users")
rows = mysql_cursor.fetchall()

# Insert into SQLite
for row in rows:
    sqlite_cursor.execute(
        "INSERT OR REPLACE INTO users (id, name, points) VALUES (?, ?, ?)",
        row
    )

sqlite_conn.commit()

# Close everything
mysql_cursor.close()
mysql_conn.close()
sqlite_cursor.close()
sqlite_conn.close()

print("✅ Migration complete.")
