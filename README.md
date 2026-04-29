# Multilingual Text-to-SQL Conversion

A Flask-based natural language to SQL system with schema-aware generation, optional similarity caching, and automatic visualization support.

## Overview

This project converts multilingual or plain-English requests into SQL queries, executes them against a SQLite database, and can render charts from the results.

### Key features

- Natural language to SQL generation
- Schema-aware prompting and entity mapping
- Optional FAISS-backed similarity cache
- SQLite query execution with structured results
- Automatic chart generation for common data shapes
- Modular backend with separate routes and services

## Repository layout

- main.py — application entry point
- backend/ — Flask app factory, routes, and services
- frontend/ — HTML, CSS, and JavaScript assets
- data/ — local database files and cached vectors
- tests/ — pytest-based test suite
- .env.example — safe template for local configuration

## Secure local development

Use a dedicated virtual environment and keep secrets out of source control.

1. Create and activate a virtual environment
2. Install dependencies from requirements.txt
3. Copy .env.example to .env
4. Add your API key and local settings
5. Run the app locally

Example configuration values:

```bash
GEMINI_API_KEY=your-gemini-api-key-here
USE_OLLAMA=false
DB_PATH=data/advanced_nlsql.db
FLASK_ENV=development
SECRET_KEY=change-me-in-prod
SIMILARITY_THRESHOLD=0.70
```

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

The server starts on http://localhost:5000 by default.

## Optional local AI backend

If you want to avoid cloud inference during development, set `USE_OLLAMA=true` and point `OLLAMA_BASE_URL` and `OLLAMA_MODEL` to a local Ollama instance.

## Testing

Run the automated tests with pytest.

```bash
pytest
```

## Configuration notes

- Do not commit `.env` or API keys
- Keep generated files such as logs, uploads, and visualizations out of source control
- Adjust `DB_PATH` to use a different SQLite database
- Tune `SIMILARITY_THRESHOLD` to make cached query matching stricter or looser

## Contributing

1. Create a feature branch
2. Make focused changes
3. Add or update tests where needed
4. Open a pull request with a short summary

