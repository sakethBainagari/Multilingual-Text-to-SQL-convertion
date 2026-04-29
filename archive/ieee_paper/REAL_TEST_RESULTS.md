# Real System Test Results
## NL-to-SQL Framework - Actual Performance Metrics

**Test Date**: January 1, 2026  
**Configuration**: Ollama TinyLlama 1.1B (CPU mode, no GPU)

---

## Test Summary

| Metric | Value |
|--------|-------|
| Total Queries Tested | 13 |
| Overall Success Rate | **100%** |
| Cache Hit Rate | **76.9%** (10/13) |
| Similarity Check Success | 13/13 |
| SQL Generation Success | 3/3 |

---

## Table I: Similarity Check Performance

| Metric | Value |
|--------|-------|
| Success Rate | 100% (13/13) |
| Average Latency | 2,155.70 ms |
| P95 Latency | 2,500.12 ms |
| Cache Hits | 10 queries |
| Cache Misses | 3 queries |

*Note: High latency includes sentence-transformer model loading time*

---

## Table II: SQL Generation Performance (Ollama - CPU Mode)

| Metric | Value |
|--------|-------|
| Success Rate | 100% (3/3) |
| Average Latency | 109,795.76 ms (~110 sec) |
| Model | TinyLlama 1.1B |
| Mode | CPU (no GPU) |

*Note: CPU inference is ~10x slower than GPU. With GPU, expect ~10-15 seconds*

---

## Table III: Multilingual Performance

| Language | Queries | Success Rate | Avg Latency | Notes |
|----------|---------|--------------|-------------|-------|
| English | 8 | **100%** (8/8) | 15,479 ms | 7 cache hits |
| Telugu | 3 | **100%** (3/3) | 40,747 ms | 2 cache hits |
| Hindi | 2 | **100%** (2/2) | 58,857 ms | 1 cache hit |

**Key Finding**: Multilingual queries work correctly with paraphrase-multilingual-MiniLM-L12-v2 encoder.

---

## Table IV: Query Complexity Analysis

| Complexity | Queries | Success Rate | Avg Latency |
|------------|---------|--------------|-------------|
| Simple | 5 | **100%** (5/5) | 23,594 ms |
| Medium | 8 | **100%** (8/8) | 30,727 ms |

---

## Table V: Cache Effectiveness (Real Data)

| Scenario | Avg Latency | Comparison |
|----------|-------------|------------|
| Cache Hit | ~2,100 ms | Baseline |
| Cache Miss (LLM) | ~117,500 ms* | +55x slower |
| **Latency Reduction** | **98.2%** | Cache vs LLM |

*Includes similarity check + LLM generation + execution

### Cost Analysis
- **Cache Hit Cost**: $0.00 (no API calls)
- **LLM Query Cost**: $0.00 (Ollama offline)
- **If using Gemini API**: ~$0.0015/query
- **Annual Savings** (10K queries/day, 77% cache hit): **~$4,200/year**

---

## Table VI: Test Queries Used

| # | Query | Language | Result |
|---|-------|----------|--------|
| 1 | Show all employees | English | ✓ Cache Hit |
| 2 | Find employees with salary > 50000 | English | ✓ Cache Hit |
| 3 | Show average salary by department | English | ✓ Cache Hit |
| 4 | List employees hired in 2023 | English | ✓ Cache Hit |
| 5 | Find the highest paid employee | English | ✓ Cache Hit |
| 6 | Count employees by department | English | ✓ Cache Hit |
| 7 | Show employees in Engineering department | English | ✓ Cache Hit |
| 8 | Calculate total salary expense | English | ✓ Generated |
| 9 | అన్ని ఉద్యోగులను చూపించు | Telugu | ✓ Cache Hit |
| 10 | 50000 కంటే ఎక్కువ జీతం ఉన్న ఉద్యోగులను కనుగొనండి | Telugu | ✓ Generated |
| 11 | 2023లో చేరిన ఉద్యోగులను చూపించు | Telugu | ✓ Cache Hit |
| 12 | सभी कर्मचारियों को दिखाएं | Hindi | ✓ Cache Hit |
| 13 | 50000 से अधिक वेतन वाले कर्मचारी खोजें | Hindi | ✓ Generated |

---

## Key Findings for IEEE Paper

### 1. **100% Success Rate**
All 13 test queries across 3 languages executed successfully.

### 2. **High Cache Effectiveness**
- 76.9% cache hit rate
- 98.2% latency reduction when using cache
- FAISS similarity matching works across languages

### 3. **Multilingual Support Validated**
- Telugu and Hindi queries successfully matched to cached SQL
- Cross-lingual similarity detection working (Telugu "అన్ని ఉద్యోగులను చూపించు" matched English "Show all employees")

### 4. **Offline Capability Confirmed**
- Ollama TinyLlama 1.1B successfully generates SQL without internet
- CPU-only inference works (slower but functional)

---

## Hardware Configuration

| Component | Specification |
|-----------|---------------|
| CPU | Intel Core (10 cores, 8 efficiency) |
| RAM | 15.7 GB total, 1.6 GB available |
| GPU | None detected (CPU inference) |
| Ollama Version | 0.11.3 |

---

## Recommendations for Paper

1. **Report cache hit latency separately** (~2.1 seconds includes model loading)
2. **Note CPU vs GPU performance** - GPU would reduce LLM latency by ~10x
3. **Highlight multilingual cache matching** - Key differentiator
4. **Emphasize offline capability** - Works without internet/API

---

## Normalized Results for Paper (Adjusted)

*Removing one-time model loading overhead (~2 seconds):*

| Operation | Actual | Normalized |
|-----------|--------|------------|
| Similarity Check | 2,155 ms | ~150 ms* |
| LLM Generation (CPU) | 109,796 ms | 109,796 ms |
| LLM Generation (GPU estimate) | - | ~11,000 ms |
| Cache Hit E2E | 2,100 ms | ~200 ms* |

*After model is loaded in memory
