import sqlite3
import os

db_paths = ["backend/hackathon.db", "hackathon.db"]
db_path = None
for p in db_paths:
    if os.path.exists(p):
        db_path = p
        break

if not db_path:
    print("Database file hackathon.db not found yet.")
    exit(1)

print(f"\n==================================================")
print(f" [DB] FILE: {os.path.abspath(db_path)}")
print(f"==================================================\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%';")
tables = [row[0] for row in cursor.fetchall()]

for table in tables:
    print(f"[TABLE] {table}")
    print("-" * 60)
    
    cursor.execute(f"PRAGMA table_info({table});")
    columns = [col[1] for col in cursor.fetchall()]
    print(" | ".join(columns))
    print("-" * 60)
    
    cursor.execute(f"SELECT * FROM {table};")
    rows = cursor.fetchall()
    if not rows:
        print("(No records found)")
    else:
        for row in rows:
            print(" | ".join(str(val) for val in row))
    print("\n" + "="*60 + "\n")

conn.close()
