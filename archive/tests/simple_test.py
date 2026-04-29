import sqlite3
import os
from dotenv import load_dotenv
import google.generativeai as genai

class TextToSQLConverter:
    def __init__(self, db_path="sample.db"):
        # Load environment variables
        load_dotenv()
        
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Please set your GEMINI_API_KEY in the .env file")
        
        genai.configure(api_key=api_key)
        
        # Test and find an available model
        available_model = self.test_available_models()
        if available_model:
            self.model = genai.GenerativeModel(available_model)
            print(f"✅ Using {available_model} model")
        else:
            raise ValueError("No compatible Gemini model available")
        
        # Initialize database
        self.db_path = db_path
        self.init_sample_database()
    
    def test_available_models(self):
        """Test which Gemini models are available"""
        print("🔍 Testing available Gemini models...")
        
        models_to_try = [
            'models/gemini-2.5-flash',           # Latest and fastest
            'models/gemini-2.5-pro',             # Most capable
            'models/gemini-flash-latest',        # Generic latest
            'models/gemini-pro-latest',          # Generic pro
            'models/gemini-2.0-flash'            # Fallback
        ]
        
        for model_name in models_to_try:
            try:
                test_model = genai.GenerativeModel(model_name)
                response = test_model.generate_content("Hello")
                print(f"✅ {model_name}: Available - {response.text[:50]}...")
                return model_name
            except Exception as e:
                print(f"❌ {model_name}: {str(e)[:100]}...")
        
        return None
    
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
            (5, 'Charlie Wilson', 'Marketing', 60000, '2022-11-05')
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
        """Get the database schema to provide context to the AI"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema_info = "Database Schema:\n"
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            schema_info += f"\nTable: {table_name}\n"
            schema_info += "Columns:\n"
            for col in columns:
                schema_info += f"  - {col[1]} ({col[2]})\n"
        
        conn.close()
        return schema_info
    
    def text_to_sql(self, natural_language_query):
        """Convert natural language to SQL using Gemini API"""
        schema = self.get_database_schema()
        
        prompt = f"""
        You are a SQL expert. Convert the following natural language query to SQL.
        
        {schema}
        
        Natural language query: "{natural_language_query}"
        
        Important guidelines:
        - Department names are stored with proper capitalization: 'Engineering', 'Marketing', 'HR'
        - Use LIKE operator with proper case or use proper capitalization in WHERE clauses
        - For department searches, use exact case matching like "department = 'Engineering'"
        - Please provide ONLY the SQL query without any explanations or markdown formatting
        - Make sure the SQL is compatible with SQLite syntax
        """
        
        try:
            response = self.model.generate_content(prompt)
            sql_query = response.text.strip()
            
            # Clean up the response (remove any markdown formatting)
            sql_query = sql_query.replace('```sql', '').replace('```', '').strip()
            
            return sql_query
        except Exception as e:
            return f"Error generating SQL: {str(e)}"
    
    def execute_sql(self, sql_query):
        """Execute SQL query and return results"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(sql_query)
            
            if sql_query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
                # Get column names
                column_names = [description[0] for description in cursor.description]
                conn.close()
                return results, column_names
            else:
                conn.commit()
                conn.close()
                return "Query executed successfully!", []
                
        except Exception as e:
            return f"Error executing SQL: {str(e)}", []
    
    def process_query(self, natural_language_query):
        """Main method to process natural language query"""
        print(f"\n🔍 Processing query: '{natural_language_query}'")
        print("-" * 50)
        
        # Convert to SQL
        sql_query = self.text_to_sql(natural_language_query)
        print(f"📝 Generated SQL: {sql_query}")
        
        # Execute SQL
        results, columns = self.execute_sql(sql_query)
        
        if isinstance(results, str):  # Error message
            print(f"❌ {results}")
        else:
            print(f"✅ Query executed successfully!")
            print(f"📊 Results:")
            
            if columns:
                # Print column headers
                header = " | ".join(f"{col:15}" for col in columns)
                print(header)
                print("-" * len(header))
                
                # Print results
                for row in results:
                    row_str = " | ".join(f"{str(val):15}" for val in row)
                    print(row_str)
                
                print(f"\n📈 Total rows: {len(results)}")
            else:
                print("No results to display.")

def main():
    try:
        converter = TextToSQLConverter()
        
        print("🚀 Text to SQL Converter")
        print("=" * 40)
        print("Sample queries you can try:")
        print("- Show all employees")
        print("- Find employees in Engineering department")
        print("- Get employees with salary greater than 70000")
        print("- Show average salary by department")
        print("- Count employees in each department")
        print("=" * 40)
        
        while True:
            user_query = input("\n💬 Enter your query (or 'quit' to exit): ").strip()
            
            if user_query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if user_query:
                converter.process_query(user_query)
            else:
                print("Please enter a valid query.")
                
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        print("Please make sure to set your GEMINI_API_KEY in the .env file")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()