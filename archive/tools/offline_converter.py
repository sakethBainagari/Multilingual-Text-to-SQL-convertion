import sqlite3
import re
from typing import List, Tuple

class OfflineTextToSQLConverter:
    """Simple offline text-to-SQL converter using pattern matching"""
    
    def __init__(self, db_path="sample.db"):
        self.db_path = db_path
        self.init_sample_database()
        self.schema = self.get_database_schema()
        
    def init_sample_database(self):
        """Create a sample database with some test data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                department TEXT NOT NULL,
                salary REAL NOT NULL,
                hire_date DATE NOT NULL
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS departments (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                budget REAL NOT NULL
            )
        ''')
        
        # Insert sample data
        cursor.execute('DELETE FROM employees')  # Clear existing data
        cursor.execute('DELETE FROM departments')
        
        # Sample employees
        employees_data = [
            (1, 'John Doe', 'Engineering', 75000, '2022-01-15'),
            (2, 'Jane Smith', 'Marketing', 65000, '2021-03-20'),
            (3, 'Bob Johnson', 'Engineering', 80000, '2020-06-10'),
            (4, 'Alice Brown', 'HR', 55000, '2023-02-28'),
            (5, 'Charlie Wilson', 'Marketing', 60000, '2022-11-05'),
            (6, 'David Lee', 'Engineering', 90000, '2021-08-15'),
            (7, 'Sarah Connor', 'Marketing', 70000, '2023-01-10')
        ]
        
        cursor.executemany('''
            INSERT INTO employees (id, name, department, salary, hire_date)
            VALUES (?, ?, ?, ?, ?)
        ''', employees_data)
        
        # Sample departments
        departments_data = [
            (1, 'Engineering', 500000),
            (2, 'Marketing', 250000),
            (3, 'HR', 150000)
        ]
        
        cursor.executemany('''
            INSERT INTO departments (id, name, budget)
            VALUES (?, ?, ?)
        ''', departments_data)
        
        conn.commit()
        conn.close()
        print("Sample database initialized successfully!")
    
    def get_database_schema(self):
        """Get the database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema = {}
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            schema[table_name] = [col[1] for col in columns]
        
        conn.close()
        return schema
    
    def text_to_sql(self, query: str) -> str:
        """Convert natural language to SQL using pattern matching"""
        query = query.lower().strip()
        
        # Pattern 1: Show/Select all from table
        if re.search(r'\b(show|list|select|get|find)\b.*\ball\b.*\b(employee|employees)\b', query):
            return "SELECT * FROM employees;"
        
        if re.search(r'\b(show|list|select|get|find)\b.*\ball\b.*\b(department|departments)\b', query):
            return "SELECT * FROM departments;"
        
        # Pattern 2: Filter by department
        if re.search(r'\b(employee|employees)\b.*\b(in|from)\b.*\b(engineering|eng)\b', query):
            return "SELECT * FROM employees WHERE department = 'Engineering';"
            
        if re.search(r'\b(employee|employees)\b.*\b(in|from)\b.*\b(marketing|market)\b', query):
            return "SELECT * FROM employees WHERE department = 'Marketing';"
            
        if re.search(r'\b(employee|employees)\b.*\b(in|from)\b.*\bhr\b', query):
            return "SELECT * FROM employees WHERE department = 'HR';"
        
        # Pattern 3: Salary filters
        salary_match = re.search(r'\bsalary\b.*\b(greater|more|above|over)\b.*?(\d+)', query)
        if salary_match:
            amount = salary_match.group(2)
            return f"SELECT * FROM employees WHERE salary > {amount};"
        
        salary_match = re.search(r'\bsalary\b.*\b(less|under|below)\b.*?(\d+)', query)
        if salary_match:
            amount = salary_match.group(2)
            return f"SELECT * FROM employees WHERE salary < {amount};"
        
        # Pattern 4: Aggregations
        if re.search(r'\b(average|avg)\b.*\bsalary\b.*\b(department|dept)\b', query):
            return "SELECT department, AVG(salary) as average_salary FROM employees GROUP BY department;"
        
        if re.search(r'\b(count|number)\b.*\b(employee|employees)\b.*\b(department|dept)\b', query):
            return "SELECT department, COUNT(*) as employee_count FROM employees GROUP BY department;"
        
        if re.search(r'\b(total|sum)\b.*\bsalary\b.*\b(department|dept)\b', query):
            return "SELECT department, SUM(salary) as total_salary FROM employees GROUP BY department;"
        
        # Pattern 5: Create table patterns
        if re.search(r'\bcreate\b.*\btable\b.*\bstudent', query):
            return '''CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY,
                roll_number INTEGER NOT NULL,
                name TEXT NOT NULL,
                marks REAL NOT NULL
            );'''
        
        # Pattern 6: Insert students
        if re.search(r'\badd\b.*\bstudent', query) or re.search(r'\binsert\b.*\bstudent', query):
            # Generate 10 students with random marks
            sql = "INSERT INTO students (roll_number, name, marks) VALUES "
            values = []
            names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack']
            marks = [85, 92, 78, 95, 88, 76, 91, 83, 89, 87]
            
            for i in range(10):
                values.append(f"({i+1}, '{names[i]} Student', {marks[i]})")
            
            return sql + ", ".join(values) + ";"
        
        # Pattern 7: Name searches
        name_match = re.search(r'\b(employee|person|worker)\b.*\b(named|called)\b.*?([a-zA-Z\s]+)', query)
        if name_match:
            name = name_match.group(3).strip()
            return f"SELECT * FROM employees WHERE name LIKE '%{name}%';"
        
        # Pattern 8: Highest/Lowest salary
        if re.search(r'\b(highest|maximum|max)\b.*\bsalary\b', query):
            return "SELECT * FROM employees ORDER BY salary DESC LIMIT 1;"
        
        if re.search(r'\b(lowest|minimum|min)\b.*\bsalary\b', query):
            return "SELECT * FROM employees ORDER BY salary ASC LIMIT 1;"
        
        # Pattern 9: Recent hires
        if re.search(r'\b(recent|new|latest)\b.*\b(hire|employee|join)', query):
            return "SELECT * FROM employees ORDER BY hire_date DESC LIMIT 5;"
        
        # Default fallback
        return f"-- Could not understand query: '{query}'\n-- Try: 'show all employees', 'find employees in engineering', 'average salary by department'"
    
    def execute_sql(self, sql_query: str) -> Tuple:
        """Execute SQL query and return results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Handle multiple statements
            statements = sql_query.split(';')
            results = None
            columns = []
            
            for statement in statements:
                statement = statement.strip()
                if not statement:
                    continue
                    
                cursor.execute(statement)
                
                if statement.upper().startswith('SELECT'):
                    results = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                else:
                    conn.commit()
                    results = "Query executed successfully!"
            
            conn.close()
            return results, columns
            
        except Exception as e:
            return f"Error executing SQL: {str(e)}", []
    
    def process_query(self, natural_language_query: str):
        """Main method to process natural language query"""
        print(f"\n🔍 Processing query: '{natural_language_query}'")
        print("🤖 Using offline pattern matching")
        print("-" * 50)
        
        # Convert to SQL
        sql_query = self.text_to_sql(natural_language_query)
        print(f"📝 Generated SQL: {sql_query}")
        
        # Execute SQL
        if not sql_query.startswith("--"):
            results, columns = self.execute_sql(sql_query)
            
            if isinstance(results, str):  # Error or success message
                print(f"✅ {results}")
            else:
                print(f"✅ Query executed successfully!")
                print(f"📊 Results:")
                
                if columns and results:
                    # Print column headers
                    header = " | ".join(f"{col:15}" for col in columns)
                    print(header)
                    print("-" * len(header))
                    
                    # Print results
                    for row in results:
                        row_str = " | ".join(f"{str(val):15}" for val in row)
                        print(row_str)
                    
                    print(f"\n📈 Total rows: {len(results)}")
                elif results == []:
                    print("No results returned.")
                else:
                    print("Query completed successfully.")
        else:
            print(f"❓ {sql_query}")

def main():
    print("🚀 Offline Text to SQL Converter")
    print("=" * 50)
    print("✅ No API keys needed - works completely offline!")
    print("✅ No quota limits - unlimited usage!")
    print()
    print("Sample queries you can try:")
    print("- Show all employees")
    print("- Find employees in Engineering department")
    print("- Get employees with salary greater than 70000")
    print("- Show average salary by department")
    print("- Count employees in each department")
    print("- Create a table with name students")
    print("- Add 10 students to students table")
    print("- Find employee with highest salary")
    print("=" * 50)
    
    converter = OfflineTextToSQLConverter()
    
    while True:
        user_query = input("\n💬 Enter your query (or 'quit' to exit): ").strip()
        
        if user_query.lower() in ['quit', 'exit', 'q']:
            print("👋 Goodbye!")
            break
        
        if user_query:
            converter.process_query(user_query)
        else:
            print("Please enter a valid query.")

if __name__ == "__main__":
    main()