"""
Simple Example Usage of Advanced NL-to-SQL System
Quick demonstration of core functionality
"""

from main import AdvancedTextToSQLConverter

def quick_demo():
    """Quick demonstration of the system"""
    print("🚀 Quick Demo - Advanced NL-to-SQL System")
    print("=" * 50)
    
    # Initialize the system
    print("Initializing system...")
    converter = AdvancedTextToSQLConverter()
    print("✅ System ready!\n")
    
    # Sample workflow
    demo_steps = [
        {
            'step': 'Creating Employee Table',
            'query': 'Create a table named employees with id, name, department, and salary'
        },
        {
            'step': 'Adding Sample Data',
            'queries': [
                'Add employee: id 1, name John Doe, department Engineering, salary 75000',
                'Add employee: id 2, name Jane Smith, department Marketing, salary 65000', 
                'Add employee: id 3, name Mike Johnson, department Engineering, salary 80000'
            ]
        },
        {
            'step': 'Querying Data',
            'query': 'Show all employees with salary greater than 70000'
        },
        {
            'step': 'Analytics with Visualization',
            'query': 'Show average salary by department',
            'visualize': True,
            'chart_type': 'bar'
        }
    ]
    
    for step_info in demo_steps:
        print(f"📋 {step_info['step']}")
        print("-" * 30)
        
        if 'queries' in step_info:
            # Multiple queries
            for query in step_info['queries']:
                result = converter.process_advanced_query(query)
                print(f"   Query: {query}")
                if result['success']:
                    print(f"   ✅ Success")
                else:
                    print(f"   ❌ Error: {result.get('error')}")
        else:
            # Single query
            query = step_info['query']
            visualize = step_info.get('visualize', False)
            chart_type = step_info.get('chart_type', None)
            
            print(f"   Query: {query}")
            result = converter.process_advanced_query(query, visualize, chart_type)
            
            if result['success']:
                print(f"   ✅ Success - {result['row_count']} rows")
                if result.get('data'):
                    print(f"   📊 Data preview: {result['data'][:2]}")
                if result.get('visualization_path'):
                    print(f"   📈 Chart saved: {result['visualization_path']}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
        
        print()
    
    # Show final database state
    schema = converter.get_comprehensive_schema()
    if schema:
        print("📊 Final Database Schema:")
        print("-" * 30)
        for table, info in schema.items():
            print(f"   Table: {table} ({info['row_count']} rows)")
            for col, col_info in info['columns'].items():
                print(f"     - {col} ({col_info['type']})")
    
    print("\n🎉 Demo completed! Check 'visualizations' folder for charts.")
    
    return converter

def interactive_mode():
    """Interactive mode for testing queries"""
    print("🔄 Interactive Mode - Advanced NL-to-SQL System")
    print("=" * 50)
    print("Type your natural language queries. Type 'quit' to exit.")
    print("Example: 'Create table products with id, name, price'")
    print()
    
    converter = AdvancedTextToSQLConverter()
    
    while True:
        try:
            query = input("💬 Your query: ").strip()
            
            if query.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not query:
                continue
                
            # Check if user wants visualization
            visualize = input("📊 Create visualization? (y/n): ").lower().startswith('y')
            chart_type = None
            
            if visualize:
                chart_type = input("📈 Chart type (bar/pie/line/histogram/scatter/auto): ").strip()
                if chart_type == 'auto' or not chart_type:
                    chart_type = None
            
            print("\n⏳ Processing...")
            result = converter.process_advanced_query(query, visualize, chart_type)
            
            if result['success']:
                print(f"✅ Success!")
                print(f"🔧 SQL: {result['sql_query']}")
                print(f"⏱️  Execution time: {result['execution_time']:.3f}s")
                
                if result.get('data') and len(result['data']) > 0:
                    print(f"📊 Rows: {result['row_count']}")
                    # Show first few rows for SELECT queries
                    if result['row_count'] <= 10:
                        import pandas as pd
                        df = pd.DataFrame(result['data'])
                        print("📋 Data:")
                        print(df.to_string(index=False))
                    else:
                        print(f"📋 First 3 rows: {result['data'][:3]}")
                        
                if result.get('visualization_path'):
                    print(f"📈 Chart: {result['visualization_path']}")
                    
            else:
                print(f"❌ Error: {result.get('error')}")
                
            print("\n" + "="*50 + "\n")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    print("Choose mode:")
    print("1. Quick Demo")
    print("2. Interactive Mode")
    
    choice = input("\nEnter choice (1-2): ").strip()
    
    if choice == "2":
        interactive_mode()
    else:
        quick_demo()