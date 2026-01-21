import sqlite3

DB_PATH = "backend/faces.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT * FROM known_people")
rows = cursor.fetchall()

print("=== Known People in Database ===")
for row in rows:
    print(f"ID: {row[0]}, Name: {row[1]}, Relation: {row[2]}")

conn.close()

#to view the faces.db (which has name, relation, person id)
