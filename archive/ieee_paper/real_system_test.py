"""
Real System Testing Script for IEEE Paper
Tests the actual NL-to-SQL system performance
"""

import requests
import time
import json
import statistics
from datetime import datetime

API_BASE = "http://localhost:5000"

# Test queries for real evaluation
TEST_QUERIES = [
    # English queries
    {"query": "Show all employees", "language": "English", "complexity": "Simple"},
    {"query": "Find employees with salary greater than 50000", "language": "English", "complexity": "Medium"},
    {"query": "Show average salary by department", "language": "English", "complexity": "Medium"},
    {"query": "List employees hired in 2023", "language": "English", "complexity": "Medium"},
    {"query": "Find the highest paid employee", "language": "English", "complexity": "Medium"},
    {"query": "Count employees by department", "language": "English", "complexity": "Medium"},
    {"query": "Show employees in Engineering department", "language": "English", "complexity": "Simple"},
    {"query": "Calculate total salary expense", "language": "English", "complexity": "Simple"},
    
    # Telugu queries
    {"query": "అన్ని ఉద్యోగులను చూపించు", "language": "Telugu", "complexity": "Simple"},
    {"query": "50000 కంటే ఎక్కువ జీతం ఉన్న ఉద్యోగులను కనుగొనండి", "language": "Telugu", "complexity": "Medium"},
    {"query": "2023లో చేరిన ఉద్యోగులను చూపించు", "language": "Telugu", "complexity": "Medium"},
    
    # Hindi queries  
    {"query": "सभी कर्मचारियों को दिखाएं", "language": "Hindi", "complexity": "Simple"},
    {"query": "50000 से अधिक वेतन वाले कर्मचारी खोजें", "language": "Hindi", "complexity": "Medium"},
]


def test_similarity_check(query: str) -> dict:
    """Test the similarity check endpoint"""
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/api/similarity-check",
            json={"query": query},
            timeout=30
        )
        latency = (time.time() - start_time) * 1000  # Convert to ms
        
        result = response.json()
        return {
            "success": result.get("success", False),
            "latency_ms": round(latency, 2),
            "similar_found": len(result.get("similar_queries", [])) > 0,
            "similarity_count": len(result.get("similar_queries", [])),
            "best_similarity": result.get("similar_queries", [{}])[0].get("similarity", 0) if result.get("similar_queries") else 0
        }
    except Exception as e:
        return {"success": False, "error": str(e), "latency_ms": 0}


def test_sql_generation(query: str, model: str = "ollama") -> dict:
    """Test SQL generation endpoint - defaults to offline Ollama"""
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/api/generate-sql",
            json={"query": query, "model": model},
            timeout=120  # Longer timeout for Ollama
        )
        latency = (time.time() - start_time) * 1000
        
        result = response.json()
        return {
            "success": result.get("success", False),
            "latency_ms": round(latency, 2),
            "sql_query": result.get("sql_query", ""),
            "model_used": result.get("model_used", model)
        }
    except Exception as e:
        return {"success": False, "error": str(e), "latency_ms": 0}


def test_sql_execution(sql_query: str, natural_query: str) -> dict:
    """Test SQL execution endpoint"""
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/api/execute-sql",
            json={
                "sql_query": sql_query,
                "natural_query": natural_query,
                "visualize": False
            },
            timeout=30
        )
        latency = (time.time() - start_time) * 1000
        
        result = response.json()
        return {
            "success": result.get("success", False),
            "latency_ms": round(latency, 2),
            "row_count": result.get("row_count", 0),
            "execution_time": result.get("execution_time", 0)
        }
    except Exception as e:
        return {"success": False, "error": str(e), "latency_ms": 0}


def run_real_tests():
    """Run tests on the actual system"""
    print("=" * 70)
    print("REAL SYSTEM EVALUATION - NL-to-SQL Framework")
    print("=" * 70)
    print(f"Testing against: {API_BASE}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check if server is running
    try:
        requests.get(f"{API_BASE}/", timeout=5)
        print("✓ Server is running")
    except:
        print("✗ Server is not running! Start with: python main.py --web")
        return
    
    results = {
        "similarity_check": [],
        "sql_generation": [],
        "sql_execution": [],
        "by_language": {"English": [], "Telugu": [], "Hindi": []},
        "by_complexity": {"Simple": [], "Medium": [], "Complex": []}
    }
    
    print("\n" + "-" * 50)
    print("Running Tests...")
    print("-" * 50)
    
    for i, test in enumerate(TEST_QUERIES, 1):
        query = test["query"]
        language = test["language"]
        complexity = test["complexity"]
        
        print(f"\n[{i}/{len(TEST_QUERIES)}] Testing: {query[:50]}...")
        
        # Test 1: Similarity Check
        sim_result = test_similarity_check(query)
        results["similarity_check"].append(sim_result)
        print(f"  Similarity: {'✓' if sim_result['success'] else '✗'} ({sim_result['latency_ms']}ms)")
        
        # Test 2: SQL Generation (only if no high similarity match)
        if sim_result.get("best_similarity", 0) < 0.9:
            gen_result = test_sql_generation(query, "ollama")  # Use Ollama for offline testing
            results["sql_generation"].append(gen_result)
            print(f"  Generation: {'✓' if gen_result['success'] else '✗'} ({gen_result['latency_ms']}ms)")
            
            # Test 3: SQL Execution
            if gen_result["success"] and gen_result.get("sql_query"):
                exec_result = test_sql_execution(gen_result["sql_query"], query)
                results["sql_execution"].append(exec_result)
                print(f"  Execution: {'✓' if exec_result['success'] else '✗'} ({exec_result['latency_ms']}ms)")
                
                # Track by language and complexity
                total_latency = sim_result["latency_ms"] + gen_result["latency_ms"] + exec_result["latency_ms"]
                results["by_language"][language].append({
                    "success": exec_result["success"],
                    "total_latency": total_latency
                })
                results["by_complexity"][complexity].append({
                    "success": exec_result["success"],
                    "total_latency": total_latency
                })
        else:
            print(f"  Using cached query (similarity: {sim_result['best_similarity']:.2%})")
            results["by_language"][language].append({
                "success": True,
                "total_latency": sim_result["latency_ms"]
            })
            results["by_complexity"][complexity].append({
                "success": True,
                "total_latency": sim_result["latency_ms"]
            })
    
    # Calculate statistics
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    # Similarity Check Stats
    sim_latencies = [r["latency_ms"] for r in results["similarity_check"] if r["success"]]
    if sim_latencies:
        print(f"\nSimilarity Check:")
        print(f"  Success Rate: {sum(1 for r in results['similarity_check'] if r['success'])}/{len(results['similarity_check'])}")
        print(f"  Avg Latency: {statistics.mean(sim_latencies):.2f} ms")
        print(f"  P95 Latency: {sorted(sim_latencies)[int(len(sim_latencies)*0.95)]:.2f} ms" if len(sim_latencies) > 1 else "")
    
    # SQL Generation Stats
    gen_latencies = [r["latency_ms"] for r in results["sql_generation"] if r["success"]]
    if gen_latencies:
        print(f"\nSQL Generation:")
        print(f"  Success Rate: {sum(1 for r in results['sql_generation'] if r['success'])}/{len(results['sql_generation'])}")
        print(f"  Avg Latency: {statistics.mean(gen_latencies):.2f} ms")
    
    # By Language Stats
    print(f"\nBy Language:")
    for lang, tests in results["by_language"].items():
        if tests:
            success_count = sum(1 for t in tests if t["success"])
            avg_latency = statistics.mean([t["total_latency"] for t in tests])
            print(f"  {lang}: {success_count}/{len(tests)} success, {avg_latency:.2f}ms avg latency")
    
    # By Complexity Stats
    print(f"\nBy Complexity:")
    for comp, tests in results["by_complexity"].items():
        if tests:
            success_count = sum(1 for t in tests if t["success"])
            avg_latency = statistics.mean([t["total_latency"] for t in tests])
            print(f"  {comp}: {success_count}/{len(tests)} success, {avg_latency:.2f}ms avg latency")
    
    # Save results
    with open("real_test_results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResults saved to: real_test_results.json")
    print("=" * 70)


if __name__ == "__main__":
    run_real_tests()
