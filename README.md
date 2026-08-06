# CodeNerva

> AI-native code intelligence platform for understanding, indexing and querying source code repositories.

CodeNerva is a backend platform designed to transform any Git repository into structured knowledge that can be explored by developers and AI agents.

Instead of relying only on embeddings, CodeNerva combines:

- Abstract Syntax Trees (Tree-sitter)
- Symbol extraction
- Knowledge Graphs
- Semantic search
- Large Language Models

The objective is to provide precise code understanding at repository scale.

---

# Current Status

🚧 Project under active development.

Current milestone:

- ✅ Project registration
- ✅ Git repository validation
- ✅ Repository cloning
- ✅ Clean Architecture
- ✅ Domain Driven Design foundations
- ✅ Unit tests

Next milestones:

- Repository snapshots
- File discovery
- Language detection
- Tree-sitter parsing
- Symbol extraction
- Chunk generation
- Embeddings
- Knowledge Graph
- Retrieval-Augmented Generation (RAG)

---

# Architecture

The project follows a layered Clean Architecture.

```
                API
                 │
        Application Layer
                 │
         Domain Layer
                 │
Infrastructure Layer
```

Main principles:

- Dependency Inversion
- Domain Driven Design
- Testability
- Explicit Use Cases
- Repository Pattern

---

# Tech Stack

Backend

- Python 3.13
- FastAPI
- Pydantic v2
- uv

Testing

- pytest
- httpx

Quality

- Ruff

Planned

- PostgreSQL
- pgvector
- Tree-sitter
- Neo4j
- OpenAI
- Docker

---

# Project Structure

```
src/
    codenerva/
        api/
        application/
        domain/
        infrastructure/

tests/

scripts/

storage/
```

---

# Running locally

Clone the repository

```bash
git clone <repository-url>
```

Install dependencies

```bash
uv sync
```

Run the API

```bash
uv run uvicorn codenerva.main:app --reload
```

Swagger

```
http://127.0.0.1:8000/docs
```

Health endpoint

```
GET /health
```

---

# Vision

Modern software projects are becoming too large for traditional navigation tools.

CodeNerva aims to build a semantic representation of an entire codebase, allowing developers and AI assistants to answer questions such as:

- Where is this business rule implemented?
- Which services call this function?
- What changed between two commits?
- Which classes are affected by this modification?
- Explain this repository before I start working on it.

Instead of searching files, developers will query knowledge.

---

# Roadmap

- [x] Project registration
- [x] Repository cloning
- [ ] Repository snapshot
- [ ] File discovery
- [ ] Language detection
- [ ] Tree-sitter parsing
- [ ] Symbol extraction
- [ ] Chunk generation
- [ ] Embeddings
- [ ] Knowledge Graph
- [ ] Semantic Retrieval
- [ ] AI Assistant

---

# License

MIT License