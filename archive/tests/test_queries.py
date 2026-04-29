"""
Test Suite for Advanced NL-to-SQL System
Comprehensive test cases covering all system functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import AdvancedTextToSQLConverter
import pandas as pd
from datetime import datetime
import unittest

class TestAdvancedNLSQL(unittest.TestCase):
    """Test cases for the advanced NL-to-SQL system"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.converter = AdvancedTextToSQLConverter(db_path="data/test_nlsql.db")
        
    def test_table_creation(self):
        """Test table creation functionality"""
        queries = [
            "Create a table named employees with id, name, department, and salary",
            "Make a new table called products with id, name, price, category",
            "Create table students with roll_no integer, name text, marks real, grade text"
        ]
        
        for query in queries:
            result = self.converter.process_advanced_query(query)
            self.assertTrue(result['success'], f"Failed to create table: {query}")
            
    def test_data_insertion(self):
        """Test data insertion functionality"""
        # Ensure tables exist
        self.test_table_creation()
        
        queries = [
            "Add employee: id 1, name John Doe, department Engineering, salary 75000",
            "Add employee: id 2, name Jane Smith, department Marketing, salary 65000",
            "Add employee: id 3, name Mike Johnson, department Engineering, salary 80000",
            "Insert product with id 1, name Laptop, price 999.99, category Electronics",
            "Add student: roll 101, name Alice, marks 95, grade A"
        ]
        
        for query in queries:
            result = self.converter.process_advanced_query(query)
            self.assertTrue(result['success'], f"Failed to insert data: {query}")
            
    def test_data_retrieval(self):
        """Test data retrieval functionality"""
        # Ensure data exists
        self.test_data_insertion()
        
        queries = [
            "Show all employees",
            "Find employees in Engineering department",
            "Display products with price greater than 500",
            "Show students with marks above 90",
            "List all employees with salary between 60000 and 80000"
        ]
        
        for query in queries:
            result = self.converter.process_advanced_query(query)
            self.assertTrue(result['success'], f"Failed to retrieve data: {query}")
            if result['data']:
                self.assertGreater(len(result['data']), 0)
                
    def test_aggregation_queries(self):
        """Test aggregation and analytical queries"""
        # Ensure data exists
        self.test_data_insertion()
        
        queries = [
            "Find average salary by department",
            "Count employees in each department",
            "Show maximum marks in each grade",
            "Display total number of products",
            "Calculate minimum salary across all employees"
        ]
        
        for query in queries:
            result = self.converter.process_advanced_query(query)
            self.assertTrue(result['success'], f"Failed aggregation query: {query}")
            
    def test_visualization_creation(self):
        """Test visualization functionality"""
        # Ensure data exists
        self.test_data_insertion()
        
        queries = [
            ("Show employee count by department", "bar"),
            ("Display salary distribution", "histogram"),
            ("Visualize grade distribution", "pie"),
            ("Show marks vs student relationship", "scatter")
        ]
        
        for query, chart_type in queries:
            result = self.converter.process_advanced_query(
                query, visualize=True, chart_type=chart_type
            )
            self.assertTrue(result['success'], f"Failed visualization: {query}")
            if result.get('visualization_path'):
                self.assertTrue(os.path.exists(result['visualization_path']))
                
    def test_similarity_matching(self):
        """Test similarity index functionality"""
        # Add some queries to build similarity index
        queries = [
            "Show all employees",
            "Display all workers",  # Similar to above
            "List employee information",  # Similar to above
            "Find products",
            "Show product list"  # Similar to above
        ]
        
        results = []
        for query in queries:
            result = self.converter.process_advanced_query(query)
            results.append(result)
            
        # Check that similar queries are found
        similar = self.converter.similarity_index.find_similar("List all employees")
        self.assertGreater(len(similar), 0, "Should find similar queries")
        
    def test_error_handling(self):
        """Test error handling for invalid queries"""
        invalid_queries = [
            "Delete everything from nowhere",  # Invalid syntax
            "Show data from nonexistent_table",  # Non-existent table
            "Create table with invalid syntax here"  # Bad syntax
        ]
        
        for query in invalid_queries:
            result = self.converter.process_advanced_query(query)
            # Should not crash, but may fail gracefully
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)

def run_sample_demonstrations():
    """Run comprehensive demonstrations of system capabilities"""
    print("🚀 Advanced NL-to-SQL System - Comprehensive Demo")
    print("=" * 60)
    
    converter = AdvancedTextToSQLConverter()
    
    # Demo categories with queries
    demo_categories = {
        "📋 Table Creation": [
            "Create a table named employees with id, name, department, salary, hire_date",
            "Make a new table called products with id, name, price, category, stock_quantity",
            "Create table customers with customer_id, name, email, phone, city"
        ],
        
        "📊 Data Insertion": [
            "Add employee: id 1, name John Doe, department Engineering, salary 75000, hire_date 2023-01-15",
            "Add employee: id 2, name Jane Smith, department Marketing, salary 65000, hire_date 2023-02-20",
            "Add employee: id 3, name Mike Johnson, department Engineering, salary 80000, hire_date 2023-01-10",
            "Add employee: id 4, name Sarah Wilson, department HR, salary 60000, hire_date 2023-03-05",
            "Insert product: id 1, name Laptop, price 999.99, category Electronics, stock 50",
            "Insert product: id 2, name Mouse, price 25.99, category Electronics, stock 200",
            "Add customer: id 1, name Alice Brown, email alice@email.com, phone 555-0101, city New York"
        ],
        
        "🔍 Basic Queries": [
            "Show all employees",
            "Find products in Electronics category",
            "Display employees with salary greater than 70000",
            "List customers from New York"
        ],
        
        "📈 Aggregation & Analytics": [
            "Calculate average salary by department",
            "Count employees in each department",  
            "Find the highest paid employee",
            "Show total value of inventory by category",
            "Display department with most employees"
        ],
        
        "📊 Visualization Queries": [
            ("Visualize employee count by department", True, "bar"),
            ("Show salary distribution across all employees", True, "histogram"),
            ("Create pie chart for department distribution", True, "pie"),
            ("Display product prices as bar chart", True, "bar")
        ],
        
        "🔗 Complex Queries": [
            "Show employees hired in 2023",
            "Find products with low stock (less than 100)",
            "List employees sorted by salary in descending order",
            "Display products with price between 20 and 1000"
        ]
    }
    
    # Execute demonstrations
    all_results = []
    
    for category, queries in demo_categories.items():
        print(f"\n{category}")
        print("-" * 40)
        
        for i, query_info in enumerate(queries, 1):
            # Handle visualization queries (tuples) vs regular queries (strings)
            if isinstance(query_info, tuple):
                query, visualize, chart_type = query_info
                print(f"{i}. {query}")
                result = converter.process_advanced_query(
                    query, visualize=visualize, chart_type=chart_type
                )
            else:
                query = query_info
                print(f"{i}. {query}")
                result = converter.process_advanced_query(query)
            
            # Display results
            if result['success']:
                print(f"   ✅ SQL: {result['sql_query'][:80]}...")
                if result.get('data') and len(result['data']) > 0:
                    print(f"   📊 Returned {result['row_count']} rows")
                    
                    # Show sample data for SELECT queries
                    if result['row_count'] > 0 and result['row_count'] <= 5:
                        print(f"   📋 Sample data: {result['data'][:2]}")
                        
                if result.get('visualization_path'):
                    print(f"   📈 Visualization: {os.path.basename(result['visualization_path'])}")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown error')}")
            
            all_results.append(result)
    
    # System Statistics
    print(f"\n📊 Session Statistics")
    print("-" * 40)
    successful_queries = sum(1 for r in all_results if r['success'])
    total_queries = len(all_results)
    print(f"Successful queries: {successful_queries}/{total_queries}")
    print(f"Success rate: {successful_queries/total_queries*100:.1f}%")
    
    # Database Schema Summary
    schema = converter.get_comprehensive_schema()
    if schema:
        print(f"\n📋 Final Database Schema:")
        print("-" * 40)
        for table, info in schema.items():
            print(f"   📊 Table: {table} ({info['row_count']} rows)")
            for col, col_info in info['columns'].items():
                print(f"      - {col} ({col_info['type']})")
    
    # Similarity Index Status
    cache_size = len(converter.similarity_index.query_cache)
    print(f"\n🧠 AI Learning Status:")
    print("-" * 40)
    print(f"Cached queries: {cache_size}")
    print(f"Vector embeddings: {len(converter.similarity_index.queries)}")
    
    print(f"\n🎉 Demo completed! Check the 'visualizations' folder for charts.")
    return converter

# Sample query collections for different use cases
SAMPLE_QUERIES = {
    "business_analytics": [
        "Create sales table with date, product, quantity, revenue",
        "Add sales record for 2024-01-15, Laptop, 5 units, 4999.95 revenue",
        "Show total revenue by product",
        "Visualize monthly sales trends"
    ],
    
    "educational": [
        "Create student grades table with student_id, subject, grade, semester",
        "Add grade record: student 101, Math, grade A, semester Fall2023",
        "Calculate average grade by subject",
        "Show grade distribution as pie chart"
    ],
    
    "inventory_management": [
        "Create inventory with item_id, name, quantity, reorder_level, supplier",
        "Add inventory item: id 1001, Widgets, quantity 150, reorder 50, supplier ABC Corp",
        "Find items below reorder level",
        "Show inventory levels by supplier"
    ],
    
    "hr_analytics": [
        "Create employee performance table with emp_id, quarter, rating, goals_met",
        "Add performance record: employee 1, Q1-2024, rating 4.5, goals 8/10",
        "Show average performance rating by quarter",
        "Visualize performance trends"
    ]
}

def run_domain_specific_tests():
    """Run domain-specific test scenarios"""
    print("🎯 Domain-Specific Scenarios")
    print("=" * 50)
    
    converter = AdvancedTextToSQLConverter()
    
    for domain, queries in SAMPLE_QUERIES.items():
        print(f"\n📊 {domain.replace('_', ' ').title()} Scenario:")
        print("-" * 30)
        
        for i, query in enumerate(queries, 1):
            print(f"{i}. {query}")
            result = converter.process_advanced_query(
                query, 
                visualize="visualize" in query.lower() or "chart" in query.lower()
            )
            
            if result['success']:
                print(f"   ✅ Success: {result['row_count']} rows affected/returned")
            else:
                print(f"   ❌ Error: {result.get('error', 'Unknown')}")

if __name__ == "__main__":
    # Run different types of tests
    
    print("Choose test mode:")
    print("1. Unit Tests")
    print("2. Comprehensive Demo") 
    print("3. Domain-Specific Tests")
    print("4. All Tests")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    if choice == "1":
        # Run unit tests
        unittest.main(argv=[''], exit=False, verbosity=2)
        
    elif choice == "2":
        # Run comprehensive demo
        run_sample_demonstrations()
        
    elif choice == "3":
        # Run domain-specific tests
        run_domain_specific_tests()
        
    elif choice == "4":
        # Run all tests
        print("Running all test suites...\n")
        unittest.main(argv=[''], exit=False, verbosity=1)
        run_sample_demonstrations()
        run_domain_specific_tests()
        
    else:
        # Default: run comprehensive demo
        print("Running comprehensive demo...\n")
        run_sample_demonstrations()