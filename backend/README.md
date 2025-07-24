# On-Prem AI Codebase Analyzer

## Structure

- `cli/`: Command-line interface entrypoint
- `indexer/`: Codebase scanning and parsing logic
- `embeddings/`: Handles embedding generation (coming soon)
- `server/`: API for RAG-based querying
- `data/`: Stores parsed JSON chunks



uvicorn server.main:app --reload --port 8000
