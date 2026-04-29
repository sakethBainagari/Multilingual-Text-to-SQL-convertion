import sqlite3

conn = sqlite3.connect('data/advanced_nlsql.db')
cursor = conn.cursor()

print('BEFORE UPDATE:')
for row in cursor.execute('SELECT id, name, age FROM employees WHERE UPPER(name) = "SAKETH"').fetchall():
    print(row)

print('\nExecuting: UPDATE employees SET age = 28 WHERE name = \'saketh\';')
cursor.execute("UPDATE employees SET age = 28 WHERE name = 'saketh'")
print(f'Rows affected: {cursor.rowcount}')
conn.commit()

print('\nAFTER UPDATE:')
for row in cursor.execute('SELECT id, name, age FROM employees WHERE UPPER(name) = "SAKETH"').fetchall():
    print(row)

conn.close()
