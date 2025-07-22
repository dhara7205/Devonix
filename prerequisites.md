# ✅ CodexPro – Customer Prerequisites

This document outlines the minimum requirements for using the CodexPro On-Prem Code Intelligence Tool in your organization.

---

## 🔐 1. Codebase Access

- ✅ Provide access to one or more local repositories.
- ✅ Ensure read permissions for all source folders to be scanned.
- ✅ Supported languages: **Python** (more coming soon).

---

## 🐍 2. Python Runtime

- ✅ Python version **3.9 or above**
- ✅ `pip` or `conda` available for dependency installation
- ✅ (Recommended) Use a virtual environment

---

## 🧠 3. Embedding Model

To generate vector embeddings for your code:

- ✅ Either host a compatible embedding model on-prem:
  - e.g., `MiniLM`, `BGE`, `InstructorEmbedding`, etc.
- ✅ Or expose an internal API for CodexPro to call like:

```http
POST /embeddings
{
  "text": "def foo(): ..."
}
```
- ❌ CodexPro does not depend on OpenAI or any external cloud service.

---

## 🗃️ 4. Vector Store (Optional for MVP)

For enabling search and RAG:

- ✅ Recommended: use **FAISS**, **Chroma**, or **Qdrant**
- ✅ Flat file-based fallback supported for testing
- ❌ No external hosting required

---

## 🖥️ 5. Hardware Requirements

| Task              | CPU | GPU |
|-------------------|-----|-----|
| Scanning          | ✅  | ❌  |
| MiniLM Embedding  | ✅  | ❌  |
| BGE Large Model   | ⚠️  | ✅  |
| RAG QA (inference)| ⚠️  | ✅  |

---

## 👤 6. Authentication (Optional for Deployment)

For enterprise usage, you may configure:

- LDAP or SSO
- Role-based access control on the RAG API

_Not required for local CLI/testing._

---

## 📑 7. Internal Policy Compliance

- ✅ CodexPro runs **fully offline**
- ✅ No telemetry or outbound API calls
- ✅ Clean logs and audit trail supported
- ✅ Custom license / SLA options available

---

## 🧰 8. Developer Infrastructure

- ✅ CLI interface for local usage
- ✅ Optional FastAPI server for team-based Q&A
- ✅ Compatible with CI/CD runners, VSCode, and Git hooks (coming soon)

---

## 📦 9. Output Format

- ✅ **JSON**: parsed chunks + metadata
- ✅ **Embeddings**: vector + metadata
- ✅ **Optional**: HTML or PDF summary reports

---

## 🧾 10. Installation & Deployment

- ✅ CLI: `python cli/main.py <path>`
- ✅ Embedding pipeline: configurable model/endpoint
- ✅ Docker container: (coming soon)
- ✅ Setup documentation included

---

## ✨ Bonus: Recommended (Not Required)

| Feature                     | Why It Helps             |
|----------------------------|--------------------------|
| Open-source integration policy | Eases security audits     |
| DevSecOps sign-off         | Smooths procurement      |
| GPU node availability      | Improves inference time  |

---

## 📬 Questions?
- Reach out to the CodexPro team or file an issue in the repo.