"""
Comprehensive Test Suite for IEEE Paper
Tests 100+ queries across multiple categories
"""

import requests
import time
import json
import statistics
from datetime import datetime

API_BASE = "http://localhost:5000"

# Comprehensive test queries - 100+ queries
TEST_QUERIES = [
    # ==================== ENGLISH QUERIES (50) ====================
    # Simple SELECT (15)
    {"query": "Show all employees", "lang": "English", "complexity": "Simple"},
    {"query": "List all departments", "lang": "English", "complexity": "Simple"},
    {"query": "Display employee names", "lang": "English", "complexity": "Simple"},
    {"query": "Get all records from employees", "lang": "English", "complexity": "Simple"},
    {"query": "Show employee table", "lang": "English", "complexity": "Simple"},
    {"query": "List employee details", "lang": "English", "complexity": "Simple"},
    {"query": "Display all staff members", "lang": "English", "complexity": "Simple"},
    {"query": "Show me everyone in the company", "lang": "English", "complexity": "Simple"},
    {"query": "Get employee list", "lang": "English", "complexity": "Simple"},
    {"query": "Fetch all employees", "lang": "English", "complexity": "Simple"},
    {"query": "View all workers", "lang": "English", "complexity": "Simple"},
    {"query": "Show complete employee data", "lang": "English", "complexity": "Simple"},
    {"query": "List all staff", "lang": "English", "complexity": "Simple"},
    {"query": "Display employee information", "lang": "English", "complexity": "Simple"},
    {"query": "Get all employee records", "lang": "English", "complexity": "Simple"},
    
    # Filtered SELECT (15)
    {"query": "Find employees with salary greater than 50000", "lang": "English", "complexity": "Medium"},
    {"query": "Show employees in Engineering department", "lang": "English", "complexity": "Medium"},
    {"query": "List employees hired after 2020", "lang": "English", "complexity": "Medium"},
    {"query": "Find employees earning less than 40000", "lang": "English", "complexity": "Medium"},
    {"query": "Show employees from HR department", "lang": "English", "complexity": "Medium"},
    {"query": "Get employees with salary between 30000 and 60000", "lang": "English", "complexity": "Medium"},
    {"query": "Find employees named John", "lang": "English", "complexity": "Medium"},
    {"query": "List employees in Sales team", "lang": "English", "complexity": "Medium"},
    {"query": "Show employees hired in 2023", "lang": "English", "complexity": "Medium"},
    {"query": "Find employees with salary above average", "lang": "English", "complexity": "Medium"},
    {"query": "Get employees from Marketing", "lang": "English", "complexity": "Medium"},
    {"query": "Show employees earning more than 70000", "lang": "English", "complexity": "Medium"},
    {"query": "List employees joined this year", "lang": "English", "complexity": "Medium"},
    {"query": "Find senior employees", "lang": "English", "complexity": "Medium"},
    {"query": "Show employees in IT department", "lang": "English", "complexity": "Medium"},
    
    # Aggregation (10)
    {"query": "Count all employees", "lang": "English", "complexity": "Medium"},
    {"query": "Show average salary", "lang": "English", "complexity": "Medium"},
    {"query": "Find total salary expense", "lang": "English", "complexity": "Medium"},
    {"query": "Count employees by department", "lang": "English", "complexity": "Medium"},
    {"query": "Show maximum salary", "lang": "English", "complexity": "Medium"},
    {"query": "Find minimum salary", "lang": "English", "complexity": "Medium"},
    {"query": "Calculate average salary by department", "lang": "English", "complexity": "Medium"},
    {"query": "Show sum of all salaries", "lang": "English", "complexity": "Medium"},
    {"query": "Count employees in each department", "lang": "English", "complexity": "Medium"},
    {"query": "Find highest paid employee", "lang": "English", "complexity": "Medium"},
    
    # Complex (10)
    {"query": "Show top 5 highest paid employees", "lang": "English", "complexity": "Complex"},
    {"query": "List employees ordered by salary descending", "lang": "English", "complexity": "Complex"},
    {"query": "Find departments with more than 5 employees", "lang": "English", "complexity": "Complex"},
    {"query": "Show average salary per department ordered by average", "lang": "English", "complexity": "Complex"},
    {"query": "List employees with above average salary in their department", "lang": "English", "complexity": "Complex"},
    {"query": "Find the second highest salary", "lang": "English", "complexity": "Complex"},
    {"query": "Show employees and their department names", "lang": "English", "complexity": "Complex"},
    {"query": "Count employees hired each year", "lang": "English", "complexity": "Complex"},
    {"query": "Find duplicate employee names", "lang": "English", "complexity": "Complex"},
    {"query": "Show salary distribution by department", "lang": "English", "complexity": "Complex"},
    
    # ==================== TELUGU QUERIES (25) ====================
    {"query": "అన్ని ఉద్యోగులను చూపించు", "lang": "Telugu", "complexity": "Simple"},
    {"query": "ఉద్యోగుల జాబితా", "lang": "Telugu", "complexity": "Simple"},
    {"query": "అన్ని విభాగాలను చూపించు", "lang": "Telugu", "complexity": "Simple"},
    {"query": "ఉద్యోగుల వివరాలు చూపించు", "lang": "Telugu", "complexity": "Simple"},
    {"query": "సిబ్బంది జాబితా", "lang": "Telugu", "complexity": "Simple"},
    {"query": "50000 కంటే ఎక్కువ జీతం ఉన్న ఉద్యోగులు", "lang": "Telugu", "complexity": "Medium"},
    {"query": "ఇంజనీరింగ్ విభాగంలో ఉద్యోగులు", "lang": "Telugu", "complexity": "Medium"},
    {"query": "2023లో చేరిన ఉద్యోగులు", "lang": "Telugu", "complexity": "Medium"},
    {"query": "అత్యధిక జీతం ఉన్న ఉద్యోగి", "lang": "Telugu", "complexity": "Medium"},
    {"query": "సగటు జీతం చూపించు", "lang": "Telugu", "complexity": "Medium"},
    {"query": "HR విభాగంలో ఉద్యోగులు", "lang": "Telugu", "complexity": "Medium"},
    {"query": "మొత్తం ఉద్యోగుల సంఖ్య", "lang": "Telugu", "complexity": "Medium"},
    {"query": "విభాగం వారీగా ఉద్యోగుల సంఖ్య", "lang": "Telugu", "complexity": "Medium"},
    {"query": "అత్యల్ప జీతం", "lang": "Telugu", "complexity": "Medium"},
    {"query": "మొత్తం జీతం ఖర్చు", "lang": "Telugu", "complexity": "Medium"},
    {"query": "సేల్స్ విభాగంలో ఉద్యోగులు", "lang": "Telugu", "complexity": "Medium"},
    {"query": "30000 కంటే తక్కువ జీతం", "lang": "Telugu", "complexity": "Medium"},
    {"query": "విభాగం వారీగా సగటు జీతం", "lang": "Telugu", "complexity": "Complex"},
    {"query": "టాప్ 5 ఉద్యోగులు జీతం ప్రకారం", "lang": "Telugu", "complexity": "Complex"},
    {"query": "ఉద్యోగుల పేర్లు మరియు విభాగాలు", "lang": "Telugu", "complexity": "Complex"},
    {"query": "ఈ సంవత్సరం చేరిన ఉద్యోగులు", "lang": "Telugu", "complexity": "Medium"},
    {"query": "మార్కెటింగ్ టీమ్ ఉద్యోగులు", "lang": "Telugu", "complexity": "Medium"},
    {"query": "IT విభాగం ఉద్యోగులు", "lang": "Telugu", "complexity": "Medium"},
    {"query": "అన్ని ఉద్యోగుల రికార్డులు", "lang": "Telugu", "complexity": "Simple"},
    {"query": "ఉద్యోగుల సమాచారం", "lang": "Telugu", "complexity": "Simple"},
    
    # ==================== HINDI QUERIES (25) ====================
    {"query": "सभी कर्मचारियों को दिखाएं", "lang": "Hindi", "complexity": "Simple"},
    {"query": "कर्मचारियों की सूची", "lang": "Hindi", "complexity": "Simple"},
    {"query": "सभी विभागों को दिखाएं", "lang": "Hindi", "complexity": "Simple"},
    {"query": "कर्मचारी विवरण", "lang": "Hindi", "complexity": "Simple"},
    {"query": "स्टाफ की सूची", "lang": "Hindi", "complexity": "Simple"},
    {"query": "50000 से अधिक वेतन वाले कर्मचारी", "lang": "Hindi", "complexity": "Medium"},
    {"query": "इंजीनियरिंग विभाग के कर्मचारी", "lang": "Hindi", "complexity": "Medium"},
    {"query": "2023 में शामिल हुए कर्मचारी", "lang": "Hindi", "complexity": "Medium"},
    {"query": "सबसे अधिक वेतन वाला कर्मचारी", "lang": "Hindi", "complexity": "Medium"},
    {"query": "औसत वेतन दिखाएं", "lang": "Hindi", "complexity": "Medium"},
    {"query": "HR विभाग के कर्मचारी", "lang": "Hindi", "complexity": "Medium"},
    {"query": "कुल कर्मचारियों की संख्या", "lang": "Hindi", "complexity": "Medium"},
    {"query": "विभाग के अनुसार कर्मचारियों की संख्या", "lang": "Hindi", "complexity": "Medium"},
    {"query": "न्यूनतम वेतन", "lang": "Hindi", "complexity": "Medium"},
    {"query": "कुल वेतन खर्च", "lang": "Hindi", "complexity": "Medium"},
    {"query": "सेल्स विभाग के कर्मचारी", "lang": "Hindi", "complexity": "Medium"},
    {"query": "30000 से कम वेतन", "lang": "Hindi", "complexity": "Medium"},
    {"query": "विभाग के अनुसार औसत वेतन", "lang": "Hindi", "complexity": "Complex"},
    {"query": "वेतन के अनुसार टॉप 5 कर्मचारी", "lang": "Hindi", "complexity": "Complex"},
    {"query": "कर्मचारी नाम और विभाग", "lang": "Hindi", "complexity": "Complex"},
    {"query": "इस वर्ष शामिल हुए कर्मचारी", "lang": "Hindi", "complexity": "Medium"},
    {"query": "मार्केटिंग टीम के कर्मचारी", "lang": "Hindi", "complexity": "Medium"},
    {"query": "IT विभाग के कर्मचारी", "lang": "Hindi", "complexity": "Medium"},
    {"query": "सभी कर्मचारी रिकॉर्ड", "lang": "Hindi", "complexity": "Simple"},
    {"query": "कर्मचारी जानकारी", "lang": "Hindi", "complexity": "Simple"},
]

def test_query(query: str) -> dict:
    """Test a single query through similarity check"""
    try:
        start_time = time.time()
        response = requests.post(
            f"{API_BASE}/api/similarity-check",
            json={"query": query},
            timeout=60
        )
        latency = (time.time() - start_time) * 1000
        
        result = response.json()
        similar = result.get("similar_queries", [])
        
        return {
            "success": result.get("success", False),
            "latency_ms": round(latency, 2),
            "cache_hit": len(similar) > 0 and similar[0].get("similarity", 0) >= 0.9,
            "best_similarity": similar[0].get("similarity", 0) if similar else 0,
            "matches_found": len(similar)
        }
    except Exception as e:
        return {"success": False, "error": str(e), "latency_ms": 0, "cache_hit": False}


def run_comprehensive_tests():
    """Run all 100 test queries"""
    print("=" * 70)
    print("COMPREHENSIVE EVALUATION - IEEE Paper Test Suite")
    print("=" * 70)
    print(f"Total Queries: {len(TEST_QUERIES)}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    # Check server
    try:
        requests.get(f"{API_BASE}/", timeout=5)
        print("✓ Server is running\n")
    except:
        print("✗ Server not running! Start with: python main.py --web")
        return
    
    results = {
        "total": len(TEST_QUERIES),
        "success": 0,
        "cache_hits": 0,
        "by_language": {"English": [], "Telugu": [], "Hindi": []},
        "by_complexity": {"Simple": [], "Medium": [], "Complex": []},
        "all_latencies": []
    }
    
    print("Running tests...\n")
    
    for i, test in enumerate(TEST_QUERIES, 1):
        query = test["query"]
        lang = test["lang"]
        complexity = test["complexity"]
        
        # Show progress every 10 queries
        if i % 10 == 0 or i == 1:
            print(f"Progress: {i}/{len(TEST_QUERIES)} ({lang})")
        
        result = test_query(query)
        
        if result["success"]:
            results["success"] += 1
            if result["cache_hit"]:
                results["cache_hits"] += 1
        
        results["all_latencies"].append(result["latency_ms"])
        results["by_language"][lang].append(result)
        results["by_complexity"][complexity].append(result)
    
    # Calculate statistics
    print("\n" + "=" * 70)
    print("RESULTS SUMMARY")
    print("=" * 70)
    
    print(f"\n📊 OVERALL METRICS:")
    print(f"  Total Queries: {results['total']}")
    print(f"  Successful: {results['success']} ({100*results['success']/results['total']:.1f}%)")
    print(f"  Cache Hits: {results['cache_hits']} ({100*results['cache_hits']/results['total']:.1f}%)")
    print(f"  Avg Latency: {statistics.mean(results['all_latencies']):.2f} ms")
    
    if len(results['all_latencies']) > 1:
        print(f"  Std Dev: {statistics.stdev(results['all_latencies']):.2f} ms")
        sorted_lat = sorted(results['all_latencies'])
        p95_idx = int(len(sorted_lat) * 0.95)
        print(f"  P95 Latency: {sorted_lat[p95_idx]:.2f} ms")
    
    print(f"\n🌍 BY LANGUAGE:")
    for lang, tests in results["by_language"].items():
        if tests:
            success = sum(1 for t in tests if t["success"])
            cache_hits = sum(1 for t in tests if t.get("cache_hit", False))
            avg_lat = statistics.mean([t["latency_ms"] for t in tests])
            print(f"  {lang}: {success}/{len(tests)} success ({100*success/len(tests):.1f}%), "
                  f"{cache_hits} cache hits, {avg_lat:.0f}ms avg")
    
    print(f"\n📈 BY COMPLEXITY:")
    for comp, tests in results["by_complexity"].items():
        if tests:
            success = sum(1 for t in tests if t["success"])
            cache_hits = sum(1 for t in tests if t.get("cache_hit", False))
            avg_lat = statistics.mean([t["latency_ms"] for t in tests])
            print(f"  {comp}: {success}/{len(tests)} success ({100*success/len(tests):.1f}%), "
                  f"{cache_hits} cache hits, {avg_lat:.0f}ms avg")
    
    # Save detailed results
    output = {
        "timestamp": datetime.now().isoformat(),
        "total_queries": results["total"],
        "success_rate": f"{100*results['success']/results['total']:.1f}%",
        "cache_hit_rate": f"{100*results['cache_hits']/results['total']:.1f}%",
        "avg_latency_ms": round(statistics.mean(results['all_latencies']), 2),
        "by_language": {
            lang: {
                "total": len(tests),
                "success": sum(1 for t in tests if t["success"]),
                "cache_hits": sum(1 for t in tests if t.get("cache_hit", False)),
                "success_rate": f"{100*sum(1 for t in tests if t['success'])/len(tests):.1f}%" if tests else "0%",
                "avg_latency": round(statistics.mean([t["latency_ms"] for t in tests]), 2) if tests else 0
            }
            for lang, tests in results["by_language"].items()
        },
        "by_complexity": {
            comp: {
                "total": len(tests),
                "success": sum(1 for t in tests if t["success"]),
                "success_rate": f"{100*sum(1 for t in tests if t['success'])/len(tests):.1f}%" if tests else "0%",
                "avg_latency": round(statistics.mean([t["latency_ms"] for t in tests]), 2) if tests else 0
            }
            for comp, tests in results["by_complexity"].items()
        }
    }
    
    with open("comprehensive_test_results.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Results saved to: comprehensive_test_results.json")
    print("=" * 70)
    
    # Print table for paper
    print("\n📋 TABLE FOR PAPER (Copy this):\n")
    print("| Language | Queries | Success Rate | Cache Hit Rate | Avg Latency |")
    print("|----------|---------|--------------|----------------|-------------|")
    for lang, data in output["by_language"].items():
        cache_rate = f"{100*data['cache_hits']/data['total']:.1f}%" if data['total'] > 0 else "0%"
        print(f"| {lang} | {data['total']} | {data['success_rate']} | {cache_rate} | {data['avg_latency']:.0f} ms |")
    
    total_cache = results['cache_hits']
    print(f"| **Total** | **{results['total']}** | **{100*results['success']/results['total']:.1f}%** | "
          f"**{100*total_cache/results['total']:.1f}%** | **{statistics.mean(results['all_latencies']):.0f} ms** |")


if __name__ == "__main__":
    run_comprehensive_tests()
