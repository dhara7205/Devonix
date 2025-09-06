# On-Prem AI Codebase Analyzer

## Structure

- `cli/`: Command-line interface entrypoint
- `indexer/`: Codebase scanning and parsing logic
- `embeddings/`: Handles embedding generation (coming soon)
- `server/`: API for RAG-based querying
- `data/`: Stores parsed JSON chunks



uvicorn server.main:app --reload --port 8000
https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={API_KEY}
