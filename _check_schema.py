import sqlite3
conn = sqlite3.connect('data/advanced_nlsql.db')
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table'")
for r in cursor.fetchall():
    if r[0]:
        print(r[0])
        print()
