# Advanced NL-to-SQL System – End-to-End Documentation

_Last updated: October 21, 2025_

This document walks through the complete project from setup to execution. It combines every feature the system offers, including the latest multilingual voice assistant. No code deep-dive is required to understand how each piece fits together.

---

## 1. Project Purpose
- Provide a natural language interface for querying structured data without SQL knowledge.
- Offer both automated SQL generation (with LLM support) and accelerated responses through similarity-based reuse.
- Deliver interactive data visualizations alongside tabular query results.
- Support voice-driven input in **Telugu**, **Hindi**, and **English**.

---

## 2. High-Level Capabilities
- **Natural Language → SQL Translation** with Gemini and local Ollama models.
- **Similarity Index & Smart Cache** using FAISS and sentence-transformer embeddings.
- **Entity Swapping & Structural Adaptation** to reuse cached SQL while adapting to new entities and column selections.
- **Voice Assistant Input** with multilingual support (te-IN, hi-IN, en-US) via the Web Speech API.
- **Interactive Web UI** with a guided workflow, progress indicators, and real-time feedback messages.
- **Dynamic Visualization Engine** that chooses suitable charts or renders requested graph types.
- **Comprehensive Logging & Persistence** for reproducibility and debugging.
- **Robust Testing Suite** covering LLM failover, vector search, entity swapping, and DML safeguards.

---

## 3. System Architecture Overview

Figure 1 illustrates the end-to-end architecture pipeline, while Figure 2 expands on the similarity adaptation loop that underpins the cache reuse logic described below.

1. **Voice Input Module (NEW)**
   - Components: microphone handler, language selector, Web Speech API, acoustic analysis, transcription, and text normalization.
   - Output: normalized text query ready for downstream processing.
2. **Input Module**
   - Accepts typed or voice-generated natural language queries.
   - Provides immediate UI validation and displays guidance.
3. **Similarity Index Module**
   - Embedding generator (all-MiniLM-L6-v2).
   - FAISS-based similarity search over persistent `query_cache.faiss` + metadata.
   - Threshold checker (default 70%) to determine reuse vs new generation.
4. **Entity Swapping Module (Enhanced)**
   - Detects numbers, strings, dates, and explicitly requested columns.
   - Adapts SQL structures (e.g., `SELECT *` → `SELECT name, age`).
   - Validates column names against schema before returning adapted SQL.
5. **LLM Selection Module**
   - Chooses between local Ollama models and cloud-based Gemini depending on user preference and availability.
6. **SQL Execution Module**
   - Validates generated SQL, executes against SQLite, formats results, and handles errors gracefully.
7. **Visualization Module**
   - Preprocesses result sets, autoselects chart types, or respects explicit user requests.
   - Renders interactive Plotly visualizations and tabular data.
8. **Result Display**
   - Presents adapted SQL, execution messages, result tables, downloads, and visualizations.
   - Offers export options (CSV, Excel) and displays process milestones.
9. **Vector Database Persistence**
   - Stores embeddings and metadata for reuse, enabling cumulative learning across sessions.

---

## 4. Detailed End-to-End Workflow

### Step 1 – Environment Preparation
1. Install Python dependencies from `requirements.txt`.
2. Configure `.env` with API keys (Gemini, optional OpenAI) and optional settings (e.g., similarity threshold).
3. Ensure data directory structure exists (`data/`, `logs/`, `visualizations/`).

### Step 2 – Server Startup
1. Launch via `python main.py --web` or choose the web interface option from the CLI menu.
2. System initializes:
   - Loads cached query embeddings and metadata.
   - Configures Gemini and optional Ollama connections.
   - Bootstraps sample SQLite schema if missing.
   - Prepares visualization directories and logging.
3. Flask server begins serving UI at `http://localhost:5000`.

### Step 3 – UI Overview
1. Step-based workflow (5 stages):
   - Enter Query (text or voice).
   - Similarity Check.
   - Model Selection (skipped automatically when cache hit is used).
   - Generated SQL Review.
   - Execution & Visualization.
2. Messaging area displays progress, warnings, or success statuses.
3. Side panel offers historical info, dataset summary, and help tips.

### Step 4 – Voice Assistant Interaction
1. User selects language (Telugu / Hindi / English) and clicks microphone icon.
2. Browser requests microphone permission; upon approval, recording begins with animated feedback.
3. Web Speech API transcribes speech and normalizes the output into the query text area.
4. User reviews transcription and proceeds as if typed.

### Step 5 – Similarity Search & Smart Cache
1. System encodes the current query into an embedding vector.
2. FAISS index retrieves nearest neighbor queries.
3. Similarity score is computed via cosine similarity (`similarity = (q · c) / (||q|| ||c||)`); if ≥ 70%:
   - Best match is selected automatically.
   - Entity Swapping Module adapts the cached SQL on the fly.
   - User sees adapted SQL instantly (~0.1s) with success messaging.
4. If similarity < 70%, control passes to the LLM Selection step.

### Step 6 – Entity Swapping & Structural Adaptation
1. Extracts numbers, quoted strings, and column mentions from both queries.
2. Swaps numerical and string entities while preserving SQL syntax (e.g., `UPPER()` cases).
3. Detects column changes; updates `SELECT` clause accordingly.
4. Returns dictionary with adapted SQL, swap status, and message (e.g., "Columns adapted and entities swapped successfully").
5. If aggregation structure differs, system warns the user and suggests generating new SQL.

### Step 7 – LLM SQL Generation (on cache miss or user request)
1. User can pick Gemini (cloud) or an Ollama model (local) from Step 3.
2. System prepares rich prompt context:
   - Full database schema with column types.
   - Sample rows and constraints.
   - Safety instructions for case-insensitive comparisons (e.g., `UPPER()`).
3. LLM returns SQL; fallback logic handles errors or rate limits (Gemini backoff with retries, rule-based fallback for deterministic patterns).
4. Rule-based shortcuts handle simple updates or counts without invoking LLM when possible.

### Step 8 – SQL Review & Manual Adjustments
1. Generated or adapted SQL displays in Step 4.
2. User may copy, edit, or confirm before execution.
3. Option to execute immediately or re-run similarity check with new phrasing.

### Step 9 – Query Execution & Visualization
1. System validates SQL to avoid destructive operations unless explicitly requested.
2. Executes against SQLite database with timing metrics.
3. Formats result table and builds visualization metadata.
4. Auto-creates chart if dataset fits heuristics (bar, line, pie, histogram, scatter) or user-specified type.
5. Displays results, visualization, and export buttons (see Figure 3 for the UI snapshot flow).
6. Records execution details for logging and optional audit trail.

### Step 10 – Persistence & Learning
1. Successful new queries are embedded and stored in FAISS index and metadata JSON.
2. Vector database persists to disk, enabling improved similarity hits over time.
3. Visualization files saved to `visualizations/` with timestamped names.
4. Logs capture detailed events under `logs/nlsql_system.log`.

### Step 11 – Voice Feature Specifics
1. Voice-only flow is identical after Step 4 (no backend changes needed).
2. UI provides status badges for listening, processing, and success states.
3. Error messages guide users if speech recognition fails or confidence is low.
4. Language selector persists selection for subsequent voice inputs.

---

## 5. Operational Guidelines
- **Clearing Cache:** Delete `data/query_cache.faiss` and `data/query_metadata.json` before restart.
- **Resetting Database:** Remove `data/advanced_nlsql.db` to regenerate fresh schema.
- **Log Analysis:** Inspect `logs/nlsql_system.log` for startup status, entity swap operations, and runtime warnings.
- **Browser Cache:** Hard refresh (Ctrl+F5) after UI updates to load new assets.

---

## 6. Testing & Validation
- **Unit Tests:** `tests/` folder covers similarity search, entity swapping, update rules, and API endpoints.
- **Manual Scenarios:**
  1. Voice query in Telugu requesting average salary per department.
  2. Text query reusing cached SQL with numeric entity changes.
  3. Column-specific query to confirm SELECT clause adaptation.
  4. Forced LLM invocation with complex aggregation.
  5. Excel/CSV export verification after execution.
- **Error Handling Checks:** Confirm UI shows warnings for aggregation structure mismatches or low speech confidence.

---

## 7. Maintenance Checklist
1. **Dependencies:** Keep Python packages updated; re-run `pip install -r requirements.txt` periodically.
2. **API Keys:** Verify `.env` keys remain valid (Gemini, optional OpenAI).
3. **Disk Usage:** Monitor growth of vector database and visualization outputs.
4. **Browser Support:** Ensure users run Chrome/Edge for voice features.
5. **Model Updates:** Refresh Ollama model list if new local models are added.
6. **Backup:** Schedule periodic backups of `data/`, `logs/`, and `visualizations/` directories.

---

## 8. Future Enhancements (Roadmap)
- Offline speech recognition for environments without cloud access.
- Wake-word activation for hands-free voice queries.
- Multi-turn conversational context retention.
- Additional database connectors beyond SQLite.
- Advanced analytics (trend detection, anomaly flags) in visualization layer.

---

## 9. Summary Checklist
- [x] Multilingual voice input (Telugu, Hindi, English).
- [x] Similarity-based smart cache with entity and column adaptation.
- [x] LLM SQL generation with robust fallback and prompt engineering.
- [x] Voice and text input pipelines unified after normalization.
- [x] Dynamic visualization and export capabilities.
- [x] Persistent vector database for cumulative learning.
- [x] Comprehensive logging, testing, and maintenance guidance.

This document serves as the definitive step-by-step reference for the entire project lifecycle. Refer to it when onboarding new contributors, presenting the architecture, or planning enhancements.
