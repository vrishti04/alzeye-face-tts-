#db1- name,relation,id(of person)
import sqlite3

def init_db():
    conn = sqlite3.connect("faces.db")
    c = conn.cursor()

    c.execute("""
    CREATE TABLE IF NOT EXISTS known_people (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        relation TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Database created successfully")
