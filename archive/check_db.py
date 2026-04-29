import sqlite3

conn = sqlite3.connect('data/advanced_nlsql.db')
print('All employees:')
for row in conn.execute('SELECT id, name, age FROM employees ORDER BY id').fetchall():
    print(row)
conn.close()
