#!/usr/bin/env python3
"""
Seed FAISS Vector Database with Common NL→SQL Query Pairs

This script pre-loads the FAISS index with common natural language queries
and their corresponding SQL templates. This allows ALL users to benefit
from similarity matching without needing LLM calls for common queries.

Supports: English, Telugu, Hindi (multilingual model)

Usage:
    python seed_faiss.py
"""

import os
import sys
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# Common NL→SQL query pairs for the employees/departments/projects schema
# Includes English, Telugu, and Hindi variations
SEED_QUERIES = [
    # === BASIC SELECT QUERIES (English) ===
    {
        "natural_query": "Show all employees",
        "sql_query": "SELECT * FROM employees;"
    },
    {
        "natural_query": "List all employees",
        "sql_query": "SELECT * FROM employees;"
    },
    {
        "natural_query": "Get all employees",
        "sql_query": "SELECT * FROM employees;"
    },
    {
        "natural_query": "Display all employees",
        "sql_query": "SELECT * FROM employees;"
    },
    
    # === TELUGU QUERIES ===
    {
        "natural_query": "అన్ని ఉద్యోగులను చూపించు",
        "sql_query": "SELECT * FROM employees;"
    },
    {
        "natural_query": "ఉద్యోగుల జాబితా చూపించు",
        "sql_query": "SELECT * FROM employees;"
    },
    {
        "natural_query": "70000 కంటే ఎక్కువ జీతం ఉన్న ఉద్యోగులను చూపించు",
        "sql_query": "SELECT * FROM employees WHERE salary > 70000;"
    },
    {
        "natural_query": "అత్యధిక జీతం ఉన్న ఉద్యోగిని చూపించు",
        "sql_query": "SELECT * FROM employees ORDER BY salary DESC LIMIT 1;"
    },
    {
        "natural_query": "విభాగం వారీగా సగటు జీతం చూపించు",
        "sql_query": "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department;"
    },
    {
        "natural_query": "ఉద్యోగుల సంఖ్య చూపించు",
        "sql_query": "SELECT COUNT(*) as total_employees FROM employees;"
    },
    {
        "natural_query": "ఇంజనీరింగ్ విభాగంలో ఉద్యోగులను చూపించు",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('Engineering');"
    },
    {
        "natural_query": "2023లో చేరిన ఉద్యోగులను చూపించు",
        "sql_query": "SELECT * FROM employees WHERE hire_date LIKE '2023%';"
    },
    
    # === HINDI QUERIES ===
    {
        "natural_query": "सभी कर्मचारियों को दिखाएं",
        "sql_query": "SELECT * FROM employees;"
    },
    {
        "natural_query": "कर्मचारियों की सूची दिखाएं",
        "sql_query": "SELECT * FROM employees;"
    },
    {
        "natural_query": "70000 से अधिक वेतन वाले कर्मचारियों को दिखाएं",
        "sql_query": "SELECT * FROM employees WHERE salary > 70000;"
    },
    {
        "natural_query": "सबसे अधिक वेतन वाले कर्मचारी को दिखाएं",
        "sql_query": "SELECT * FROM employees ORDER BY salary DESC LIMIT 1;"
    },
    {
        "natural_query": "विभाग के अनुसार औसत वेतन दिखाएं",
        "sql_query": "SELECT department, AVG(salary) as avg_salary FROM employees GROUP BY department;"
    },
    {
        "natural_query": "कर्मचारियों की संख्या दिखाएं",
        "sql_query": "SELECT COUNT(*) as total_employees FROM employees;"
    },
    {
        "natural_query": "इंजीनियरिंग विभाग के कर्मचारियों को दिखाएं",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('Engineering');"
    },
    {
        "natural_query": "2023 में जुड़े कर्मचारियों को दिखाएं",
        "sql_query": "SELECT * FROM employees WHERE hire_date LIKE '2023%';"
    },
    
    # === ENGLISH QUERIES (continued) ===
    {
        "natural_query": "Show all departments",
        "sql_query": "SELECT * FROM departments;"
    },
    {
        "natural_query": "List all departments",
        "sql_query": "SELECT * FROM departments;"
    },
    {
        "natural_query": "Show all projects",
        "sql_query": "SELECT * FROM projects;"
    },
    {
        "natural_query": "List all projects",
        "sql_query": "SELECT * FROM projects;"
    },
    
    # === SALARY FILTERS ===
    {
        "natural_query": "Show all employees with salary greater than 70000",
        "sql_query": "SELECT * FROM employees WHERE salary > 70000;"
    },
    {
        "natural_query": "Show employees with salary greater than 50000",
        "sql_query": "SELECT * FROM employees WHERE salary > 50000;"
    },
    {
        "natural_query": "Show employees with salary greater than 60000",
        "sql_query": "SELECT * FROM employees WHERE salary > 60000;"
    },
    {
        "natural_query": "Show employees with salary greater than 80000",
        "sql_query": "SELECT * FROM employees WHERE salary > 80000;"
    },
    {
        "natural_query": "Show employees with salary greater than 100000",
        "sql_query": "SELECT * FROM employees WHERE salary > 100000;"
    },
    {
        "natural_query": "Show employees with salary less than 50000",
        "sql_query": "SELECT * FROM employees WHERE salary < 50000;"
    },
    {
        "natural_query": "Show employees with salary less than 60000",
        "sql_query": "SELECT * FROM employees WHERE salary < 60000;"
    },
    {
        "natural_query": "Find employees earning more than 70000",
        "sql_query": "SELECT * FROM employees WHERE salary > 70000;"
    },
    {
        "natural_query": "List employees with high salary",
        "sql_query": "SELECT * FROM employees WHERE salary > 70000 ORDER BY salary DESC;"
    },
    {
        "natural_query": "Show employees with salary between 50000 and 80000",
        "sql_query": "SELECT * FROM employees WHERE salary BETWEEN 50000 AND 80000;"
    },
    
    # === DEPARTMENT FILTERS ===
    {
        "natural_query": "Show employees in Engineering department",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('Engineering');"
    },
    {
        "natural_query": "Show employees in HR department",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('HR');"
    },
    {
        "natural_query": "Show employees in Sales department",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('Sales');"
    },
    {
        "natural_query": "Show employees in Marketing department",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('Marketing');"
    },
    {
        "natural_query": "Show employees in Finance department",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('Finance');"
    },
    {
        "natural_query": "List all Engineering employees",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('Engineering');"
    },
    {
        "natural_query": "Find employees working in Sales",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('Sales');"
    },
    
    # === COUNT QUERIES ===
    {
        "natural_query": "Count all employees",
        "sql_query": "SELECT COUNT(*) as total_employees FROM employees;"
    },
    {
        "natural_query": "How many employees are there",
        "sql_query": "SELECT COUNT(*) as total_employees FROM employees;"
    },
    {
        "natural_query": "Total number of employees",
        "sql_query": "SELECT COUNT(*) as total_employees FROM employees;"
    },
    {
        "natural_query": "Count employees in Engineering department",
        "sql_query": "SELECT COUNT(*) as count FROM employees WHERE UPPER(department) = UPPER('Engineering');"
    },
    {
        "natural_query": "Count employees in Sales department",
        "sql_query": "SELECT COUNT(*) as count FROM employees WHERE UPPER(department) = UPPER('Sales');"
    },
    {
        "natural_query": "How many employees in HR",
        "sql_query": "SELECT COUNT(*) as count FROM employees WHERE UPPER(department) = UPPER('HR');"
    },
    {
        "natural_query": "Count employees by department",
        "sql_query": "SELECT department, COUNT(*) as employee_count FROM employees GROUP BY department;"
    },
    {
        "natural_query": "Number of employees per department",
        "sql_query": "SELECT department, COUNT(*) as employee_count FROM employees GROUP BY department;"
    },
    
    # === AVERAGE/SUM QUERIES ===
    {
        "natural_query": "Find average salary",
        "sql_query": "SELECT AVG(salary) as average_salary FROM employees;"
    },
    {
        "natural_query": "What is the average salary",
        "sql_query": "SELECT AVG(salary) as average_salary FROM employees;"
    },
    {
        "natural_query": "Average salary by department",
        "sql_query": "SELECT department, AVG(salary) as average_salary FROM employees GROUP BY department;"
    },
    {
        "natural_query": "Find average salary by department",
        "sql_query": "SELECT department, AVG(salary) as average_salary FROM employees GROUP BY department;"
    },
    {
        "natural_query": "Show average salary for each department",
        "sql_query": "SELECT department, AVG(salary) as average_salary FROM employees GROUP BY department;"
    },
    {
        "natural_query": "Total salary expense",
        "sql_query": "SELECT SUM(salary) as total_salary FROM employees;"
    },
    {
        "natural_query": "Sum of all salaries",
        "sql_query": "SELECT SUM(salary) as total_salary FROM employees;"
    },
    {
        "natural_query": "Total salary by department",
        "sql_query": "SELECT department, SUM(salary) as total_salary FROM employees GROUP BY department;"
    },
    
    # === MAX/MIN QUERIES ===
    {
        "natural_query": "Find highest salary",
        "sql_query": "SELECT MAX(salary) as highest_salary FROM employees;"
    },
    {
        "natural_query": "What is the maximum salary",
        "sql_query": "SELECT MAX(salary) as maximum_salary FROM employees;"
    },
    {
        "natural_query": "Find lowest salary",
        "sql_query": "SELECT MIN(salary) as lowest_salary FROM employees;"
    },
    {
        "natural_query": "What is the minimum salary",
        "sql_query": "SELECT MIN(salary) as minimum_salary FROM employees;"
    },
    {
        "natural_query": "Show employee with highest salary",
        "sql_query": "SELECT * FROM employees ORDER BY salary DESC LIMIT 1;"
    },
    {
        "natural_query": "Who has the highest salary",
        "sql_query": "SELECT * FROM employees ORDER BY salary DESC LIMIT 1;"
    },
    {
        "natural_query": "Top 5 highest paid employees",
        "sql_query": "SELECT * FROM employees ORDER BY salary DESC LIMIT 5;"
    },
    {
        "natural_query": "Top 10 employees by salary",
        "sql_query": "SELECT * FROM employees ORDER BY salary DESC LIMIT 10;"
    },
    
    # === ORDER BY QUERIES ===
    {
        "natural_query": "Show employees ordered by salary",
        "sql_query": "SELECT * FROM employees ORDER BY salary DESC;"
    },
    {
        "natural_query": "List employees by salary descending",
        "sql_query": "SELECT * FROM employees ORDER BY salary DESC;"
    },
    {
        "natural_query": "Show employees sorted by name",
        "sql_query": "SELECT * FROM employees ORDER BY name ASC;"
    },
    {
        "natural_query": "List employees alphabetically",
        "sql_query": "SELECT * FROM employees ORDER BY name ASC;"
    },
    {
        "natural_query": "Show employees ordered by hire date",
        "sql_query": "SELECT * FROM employees ORDER BY hire_date DESC;"
    },
    {
        "natural_query": "Show newest employees",
        "sql_query": "SELECT * FROM employees ORDER BY hire_date DESC LIMIT 10;"
    },
    {
        "natural_query": "Show oldest employees by hire date",
        "sql_query": "SELECT * FROM employees ORDER BY hire_date ASC LIMIT 10;"
    },
    
    # === NAME SEARCH ===
    {
        "natural_query": "Find employee named John",
        "sql_query": "SELECT * FROM employees WHERE UPPER(name) LIKE UPPER('%John%');"
    },
    {
        "natural_query": "Search for employee Smith",
        "sql_query": "SELECT * FROM employees WHERE UPPER(name) LIKE UPPER('%Smith%');"
    },
    {
        "natural_query": "Find employees with name containing Kumar",
        "sql_query": "SELECT * FROM employees WHERE UPPER(name) LIKE UPPER('%Kumar%');"
    },
    
    # === PROJECT QUERIES ===
    {
        "natural_query": "Show all active projects",
        "sql_query": "SELECT * FROM projects WHERE UPPER(status) = UPPER('Active');"
    },
    {
        "natural_query": "List projects in progress",
        "sql_query": "SELECT * FROM projects WHERE UPPER(status) = UPPER('In Progress');"
    },
    {
        "natural_query": "Show completed projects",
        "sql_query": "SELECT * FROM projects WHERE UPPER(status) = UPPER('Completed');"
    },
    {
        "natural_query": "Find projects with budget greater than 100000",
        "sql_query": "SELECT * FROM projects WHERE budget > 100000;"
    },
    {
        "natural_query": "Show projects ordered by budget",
        "sql_query": "SELECT * FROM projects ORDER BY budget DESC;"
    },
    
    # === EXPERIENCE QUERIES ===
    {
        "natural_query": "Show employees with more than 5 years experience",
        "sql_query": "SELECT * FROM employees WHERE experience_years > 5;"
    },
    {
        "natural_query": "Find employees with experience greater than 3 years",
        "sql_query": "SELECT * FROM employees WHERE experience_years > 3;"
    },
    {
        "natural_query": "List senior employees with 10 years experience",
        "sql_query": "SELECT * FROM employees WHERE experience_years >= 10;"
    },
    {
        "natural_query": "Show junior employees",
        "sql_query": "SELECT * FROM employees WHERE experience_years < 3;"
    },
    
    # === AGE QUERIES ===
    {
        "natural_query": "Show employees older than 30",
        "sql_query": "SELECT * FROM employees WHERE age > 30;"
    },
    {
        "natural_query": "Find employees younger than 25",
        "sql_query": "SELECT * FROM employees WHERE age < 25;"
    },
    {
        "natural_query": "List employees between 25 and 35 years old",
        "sql_query": "SELECT * FROM employees WHERE age BETWEEN 25 AND 35;"
    },
    
    # === COMBINED FILTERS ===
    {
        "natural_query": "Show Engineering employees with salary greater than 70000",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('Engineering') AND salary > 70000;"
    },
    {
        "natural_query": "Find Sales employees earning more than 60000",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('Sales') AND salary > 60000;"
    },
    {
        "natural_query": "List HR employees with more than 5 years experience",
        "sql_query": "SELECT * FROM employees WHERE UPPER(department) = UPPER('HR') AND experience_years > 5;"
    },
    
    # === DISTINCT QUERIES ===
    {
        "natural_query": "Show all unique departments",
        "sql_query": "SELECT DISTINCT department FROM employees;"
    },
    {
        "natural_query": "List distinct departments",
        "sql_query": "SELECT DISTINCT department FROM employees;"
    },
    {
        "natural_query": "What departments exist",
        "sql_query": "SELECT DISTINCT department FROM employees;"
    },
]


def seed_faiss():
    """Load seed queries into FAISS index"""
    from main import AdvancedTextToSQLConverter
    
    print("=" * 60)
    print("FAISS Seeding Script")
    print("=" * 60)
    
    # Initialize converter (loads existing FAISS index)
    print("\n[1/4] Initializing converter...")
    converter = AdvancedTextToSQLConverter()
    
    existing_count = len(converter.similarity_index.queries)
    print(f"      Existing queries in FAISS: {existing_count}")
    
    # Get existing queries to avoid duplicates
    existing_queries = set(
        q['natural_query'].lower().strip() 
        for q in converter.similarity_index.queries
    )
    
    # Add new queries
    print(f"\n[2/4] Adding seed queries...")
    added = 0
    skipped = 0
    
    for item in SEED_QUERIES:
        nq = item['natural_query'].lower().strip()
        if nq not in existing_queries:
            converter.similarity_index.add_query(
                query=item['natural_query'],
                sql=item['sql_query'],
                result_metadata={
                    'source': 'seed_script',
                    'seeded_at': datetime.now().isoformat()
                }
            )
            existing_queries.add(nq)
            added += 1
            print(f"      + Added: {item['natural_query'][:50]}...")
        else:
            skipped += 1
    
    print(f"\n[3/4] Summary:")
    print(f"      - Added: {added} new queries")
    print(f"      - Skipped (duplicates): {skipped}")
    print(f"      - Total in FAISS: {len(converter.similarity_index.queries)}")
    
    # Test similarity search
    print(f"\n[4/4] Testing similarity search...")
    test_queries = [
        "Show all employees with salary greater than 90000",
        "Count employees in Marketing",
        "What is the average salary by department",
    ]
    
    for tq in test_queries:
        results = converter.similarity_index.find_similar(tq, k=1, threshold=0.5)
        if results:
            print(f"\n      Query: '{tq}'")
            print(f"      Match: '{results[0]['natural_query'][:50]}...' ({results[0]['similarity']*100:.1f}%)")
        else:
            print(f"\n      Query: '{tq}'")
            print(f"      Match: No similar query found")
    
    print("\n" + "=" * 60)
    print("Seeding complete! FAISS index saved to disk.")
    print("=" * 60)


if __name__ == "__main__":
    seed_faiss()
