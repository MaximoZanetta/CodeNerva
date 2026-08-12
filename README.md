# CodeNerva

> AI-native code intelligence platform for understanding, indexing, and querying software repositories.

CodeNerva transforms source code repositories into structured knowledge that can be explored by developers and AI systems.

Rather than relying exclusively on vector similarity, CodeNerva combines static code analysis, semantic retrieval, graph-based relationships, and Large Language Models to reason about code at repository scale.

The long-term goal is to help developers understand unfamiliar codebases, trace execution flows, explore dependencies, and answer architectural questions without manually navigating hundreds or thousands of files.

---

## Why CodeNerva?

Understanding an unfamiliar codebase is difficult.

A developer joining an existing project often needs to answer questions such as:

- Where does a request enter the system?
- Which functions participate in this workflow?
- Where is a business rule validated?
- What calls this function?
- Which files depend on this module?
- How does a flow cross frontend and backend boundaries?
- What parts of the system could be affected by a change?

Traditional code search is useful for finding text, while embedding-based RAG can retrieve semantically similar code.

CodeNerva goes further by combining semantic similarity with the structural relationships extracted directly from the source code.

```text
Repository
    │
    ▼
File Discovery
    │
    ▼
Language Detection
    │
    ▼
Tree-sitter Parsing
    │
    ├──────────────► Symbols
    │                  │
    │                  ▼
    │              Code Chunks
    │                  │
    │                  ▼
    │              Embeddings
    │                  │
    │                  ▼
    │              Vector Search
    │
    ├──────────────► Imports
    │
    └──────────────► Code Relations
                       │
                       ▼
                  Knowledge Graph
                       │
                ┌──────┴──────┐
                │             │
          Semantic Search  Graph Expansion
                │             │
                └──────┬──────┘
                       ▼
                Hybrid Reranking
                       │
                       ▼
                  Context Budget
                       │
                       ▼
                      LLM
                       │
                       ▼
                     Answer
```

The LLM is therefore not expected to discover the repository structure by itself. CodeNerva builds that structure before asking the model to reason over the relevant evidence.

---

## Current Status

🚧 **CodeNerva is under active development.**

The current prototype supports an end-to-end persistent repository intelligence pipeline.

### Repository ingestion

- ✅ Project registration
- ✅ Git repository validation
- ✅ Repository cloning
- ✅ Repository snapshots
- ✅ Source file discovery
- ✅ Content hashing
- ✅ Programming language detection
- ✅ Repository-wide analysis

### Static code analysis

- ✅ Tree-sitter parsing
- ✅ Multi-language parsing architecture
- ✅ Symbol extraction
- ✅ Functions and classes
- ✅ Nested symbols
- ✅ Qualified symbol names
- ✅ Import extraction
- ✅ Local import resolution
- ✅ TypeScript path alias resolution
- ✅ Cross-file relationships
- ✅ Function call extraction
- ✅ Cross-file call resolution
- ✅ `CALLS` / `CALLED_BY` graph traversal

### Retrieval

- ✅ Symbol-aware code chunking
- ✅ Embedding generation
- ✅ Vector records
- ✅ Semantic search
- ✅ Snapshot-scoped semantic search
- ✅ Knowledge-graph expansion
- ✅ Hybrid retrieval
- ✅ Hybrid reranking
- ✅ Context deduplication
- ✅ Context budgeting

### Repository QA

- ✅ Repository-wide indexing
- ✅ Retrieval context generation
- ✅ LLM-based repository questions
- ✅ Multi-file reasoning
- ✅ Cross-language flow explanation
- ✅ Snapshot-scoped repository questions

### Persistence

- ✅ PostgreSQL persistence
- ✅ Persistent projects
- ✅ Persistent repositories
- ✅ Persistent snapshots
- ✅ Persistent source files
- ✅ Persistent symbols
- ✅ Persistent import references
- ✅ Persistent source-file relationships
- ✅ Persistent symbol relationships
- ✅ Persistent chunks
- ✅ Qdrant vector persistence
- ✅ Snapshot-scoped vector retrieval
- ✅ Repository QA across API restarts

CodeNerva can currently analyze and answer questions across code written in languages such as Python, JavaScript, TypeScript, and TSX, with the parsing architecture designed to be extended to additional languages.

---

## Example

After analyzing and indexing a repository, a developer can ask:

```text
How does streaming work end-to-end from the React client
to the Python backend?
```

CodeNerva can retrieve relevant symbols from different files and languages and reconstruct a flow such as:

```text
React client

handleClick
    │
    ▼
handleStreamingChat
    │
    ▼
fetchStreamData
    │
    │ HTTP streaming request
    ▼

Python backend

stream
    │
    ▼
generate
    │
    ▼
Streaming model response
```

The final answer is generated from the retrieved source code and structural relationships rather than from vector similarity alone.

---

## Architecture

CodeNerva follows a layered Clean Architecture.

```text
                 API
                  │
                  ▼
           Application Layer
                  │
                  ▼
              Domain Layer
                  ▲
                  │
          Infrastructure Layer
```

The project is built around explicit boundaries between domain concepts and infrastructure.

Main principles:

- Clean Architecture
- Dependency Inversion
- Domain Driven Design foundations
- Explicit application use cases
- Repository / Store abstractions
- Infrastructure-independent domain models
- Testability
- Deterministic IDs where appropriate
- Replaceable external providers
- Persistent repository intelligence

External systems such as embedding providers, vector databases, relational databases, and LLM providers are accessed through abstractions so they can be replaced without coupling the core application logic to a specific vendor.

---

## Retrieval Architecture

CodeNerva currently combines two complementary retrieval strategies.

### Semantic Retrieval

Source code is chunked around semantic units such as functions and methods.

Each chunk contains metadata such as:

```text
Snapshot
Language
File
Qualified symbol name
Symbol kind
Source code
```

Embeddings allow CodeNerva to find code that is semantically related to a natural-language question.

Semantic searches are scoped by repository snapshot, preventing results from unrelated repository versions from being mixed.

### Graph Retrieval

Static analysis creates relationships between code entities.

Examples include:

```text
CALLS
CALLED_BY
IMPORTS
CONTAINS
```

These relationships allow CodeNerva to expand beyond the initial semantic matches and retrieve structurally related code.

### Hybrid Retrieval

The two strategies are combined:

```text
Question
   │
   ▼
Snapshot-scoped
Semantic Search
   │
   ▼
Initial Symbols
   │
   ▼
Graph Expansion
   │
   ▼
Hybrid Reranking
   │
   ▼
Context Budget
   │
   ▼
LLM
```

This makes it possible to retrieve code that may not be semantically similar to the original question but is essential to understanding the execution flow.

---

## Persistent Repository Intelligence

CodeNerva persists the repository representation instead of keeping repository intelligence only in application memory.

Structured repository knowledge is stored in PostgreSQL:

```text
PostgreSQL
├── Projects
├── Repositories
├── Snapshots
├── Source Files
├── Symbols
├── Import References
├── Source File Relations
├── Symbol Relations
└── Chunks
```

Vector representations are stored separately in Qdrant:

```text
Qdrant
└── Vector Records
    ├── Embeddings
    ├── Snapshot metadata
    ├── Source file metadata
    └── Symbol metadata
```

This separation allows CodeNerva to reconstruct its repository intelligence pipeline after an application restart without requiring the repository to be analyzed and indexed again.

```text
PostgreSQL                Qdrant
     │                       │
Structured Knowledge     Embeddings
     │                       │
     └──────────┬────────────┘
                ▼
        Hybrid Retrieval
                │
                ▼
        Context Generation
                │
                ▼
               LLM
                │
                ▼
              Answer
```

Repository questions therefore operate over persisted repository intelligence rather than process-local application state.

---

## Snapshot Isolation

CodeNerva models repositories through commit-based snapshots.

Semantic retrieval is explicitly scoped by `snapshot_id`.

```text
Question
   │
   ▼
snapshot_id
   │
   ▼
Vector Search
   │
   ▼
Qdrant Payload Filter
   │
   ▼
Only vectors belonging
to the requested snapshot
```

This prevents semantic results from different repositories or different versions of the same repository from being mixed during retrieval.

Snapshot isolation also provides the foundation for future capabilities such as:

- Incremental indexing
- Snapshot comparison
- Change-impact analysis
- Historical repository exploration

---

## Persistence Architecture

CodeNerva separates structured repository knowledge from vector retrieval infrastructure.

```text
                         CodeNerva
                             │
                ┌────────────┴────────────┐
                │                         │
                ▼                         ▼
           PostgreSQL                  Qdrant
                │                         │
                ├── Projects              └── Embeddings
                ├── Repositories              + metadata
                ├── Snapshots
                ├── Source Files
                ├── Symbols
                ├── Imports
                ├── File Relations
                ├── Symbol Relations
                └── Chunks
```

PostgreSQL acts as the persistent source of structured repository intelligence.

Qdrant stores the vector representation required for semantic retrieval.

The two representations are connected through stable identifiers and snapshot metadata.

---

## Tech Stack

### Backend

- Python 3.13
- FastAPI
- Pydantic v2
- uv

### Code Analysis

- Tree-sitter
- Language-specific parsers
- Static symbol extraction
- Import resolution
- Call graph construction

### AI / Retrieval

- OpenAI embeddings
- OpenAI LLM integration
- Semantic vector search
- Graph-enhanced retrieval
- Hybrid retrieval
- Hybrid reranking
- Context budgeting

### Persistence

- PostgreSQL
- SQLAlchemy
- Qdrant

### Testing

- pytest
- httpx
- Deterministic test embedding provider
- In-memory infrastructure implementations

### Code Quality

- Ruff

### Planned Infrastructure

- Database migrations
- Docker

---

## Project Structure

```text
src/
└── codenerva/
    ├── api/
    ├── application/
    │   ├── chunking/
    │   ├── embeddings/
    │   ├── parsing/
    │   ├── qa/
    │   └── retrieval/
    ├── domain/
    └── infrastructure/
        └── database/

tests/
├── api/
├── application/
├── domain/
├── infrastructure/
└── integration/

scripts/

storage/
├── repositories/
└── qdrant/
```

---

## Running Locally

Clone the repository:

```bash
git clone <repository-url>
cd CodeNerva
```

Install dependencies:

```bash
uv sync
```

Configure the required environment variables.

For PostgreSQL persistence:

```text
DATABASE_URL=postgresql+psycopg://<user>:<password>@localhost:5432/codenerva
```

For OpenAI-backed embeddings and repository QA:

```text
OPENAI_API_KEY=your-api-key
```

Do not commit credentials or local environment files containing secrets.

Initialize the PostgreSQL database:

```bash
uv run python scripts/init_database.py
```

Run the API:

```bash
uv run uvicorn codenerva.main:app --reload
```

Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
GET /health
```

Run the test suite:

```bash
uv run pytest
```

Run linting:

```bash
uv run ruff check .
```

Format the code:

```bash
uv run ruff format .
```

---

## Current End-to-End Flow

The current development flow is:

```text
Register Project
      │
      ▼
Register Repository
      │
      ▼
Create Snapshot
      │
      ▼
Clone Repository
      │
      ▼
Discover Files
      │
      ▼
Analyze Snapshot
      │
      ├── Parse source code
      ├── Extract symbols
      ├── Extract imports
      ├── Resolve local imports
      ├── Build file relationships
      └── Build call relationships
      │
      ▼
Persist Repository Intelligence
      │
      └── PostgreSQL
      │
      ▼
Index Snapshot
      │
      ├── Generate symbol chunks
      ├── Persist chunks
      ├── Generate embeddings
      └── Store vectors in Qdrant
      │
      ▼
Ask Repository Question
      │
      ├── Filter retrieval by snapshot
      ├── Semantic retrieval
      ├── Graph expansion
      ├── Hybrid reranking
      ├── Context budgeting
      └── LLM answer generation
```

After repository intelligence has been persisted, CodeNerva can answer questions after an application restart without rebuilding the repository representation.

---

## Repository Question Flow

A repository question currently travels through the following pipeline:

```text
Question + snapshot_id
        │
        ▼
Query Embedding
        │
        ▼
Qdrant Search
        │
        │ snapshot_id filter
        ▼
Semantic Hits
        │
        ▼
Symbol Resolution
        │
        ▼
Graph Expansion
        │
        ▼
Hybrid Reranking
        │
        ▼
Context Builder
        │
        ▼
Deduplication
        │
        ▼
Character / Item Budget
        │
        ▼
Prompt Construction
        │
        ▼
LLM
        │
        ▼
Repository-grounded Answer
```

This architecture keeps retrieval responsibilities separate from answer generation.

---

## Vision

Modern software systems are often too large to understand through manual navigation alone.

CodeNerva aims to build a continuously queryable representation of an entire codebase.

A developer joining an unfamiliar project should eventually be able to provide a repository and ask:

> Explain the architecture of this repository and tell me where I should start reading.

Or:

> Trace what happens from the moment a user confirms a purchase until the payment is processed.

Or:

> If I modify this function, what parts of the system could be affected?

The goal is to turn repository exploration from:

```text
search → open file → search → open file → trace manually
```

into:

```text
question → structural investigation → evidence → explanation
```

---

## Product Direction

One of the primary use cases being explored is **developer onboarding into large, unfamiliar codebases**.

Potential applications include:

- Repository onboarding
- Architecture exploration
- Execution-flow tracing
- Dependency analysis
- Change-impact analysis
- AI-assisted codebase navigation
- Engineering knowledge discovery

A possible onboarding workflow is:

```text
New Developer
      │
      ▼
Existing Repository
      │
      ▼
CodeNerva
      │
      ├── Understand architecture
      ├── Trace execution flows
      ├── Discover dependencies
      ├── Locate business rules
      └── Ask repository questions
```

CodeNerva is currently a development-stage prototype and is not yet intended for production repository workloads.

---

## Roadmap

### Core Intelligence

- [x] Project registration
- [x] Repository registration
- [x] Repository cloning
- [x] Repository snapshots
- [x] File discovery
- [x] Content hashing
- [x] Language detection
- [x] Tree-sitter parsing
- [x] Symbol extraction
- [x] Import extraction
- [x] Local import resolution
- [x] TypeScript path alias resolution
- [x] Call graph extraction
- [x] Cross-file call resolution
- [x] Symbol-aware chunking
- [x] Embeddings
- [x] Semantic retrieval
- [x] Knowledge-graph expansion
- [x] Hybrid retrieval
- [x] Hybrid reranking
- [x] Context budgeting
- [x] Repository-wide indexing
- [x] Repository QA

### Infrastructure

- [x] PostgreSQL persistence
- [x] Persistent projects
- [x] Persistent repositories
- [x] Persistent snapshots
- [x] Persistent source files
- [x] Persistent symbols
- [x] Persistent imports
- [x] Persistent source-file relationships
- [x] Persistent symbol relationships
- [x] Persistent repository graph
- [x] Persistent chunks
- [x] Qdrant vector persistence
- [x] Snapshot-scoped vector retrieval
- [x] Repository QA across application restarts
- [x] Incremental indexing
- [ ] Snapshot-aware vector lifecycle
- [ ] Database migrations
- [ ] Docker environment

### Code Intelligence

- [ ] Architecture-level repository analysis
- [ ] Entrypoint detection
- [ ] Module / subsystem discovery
- [ ] Additional graph relation types
- [ ] Change-impact analysis
- [ ] Test-to-production-code relationships
- [ ] Repository-level summaries
- [ ] Improved multi-language coverage

### Retrieval & Evaluation

- [ ] Incremental embedding generation
- [x] Reuse unchanged files through content hashes
- [ ] Retrieval evaluation dataset
- [ ] Retrieval quality benchmarks
- [ ] Larger repository evaluation
- [ ] Retrieval tracing and diagnostics
- [ ] Context quality evaluation

### Product

- [ ] GitHub integration
- [ ] Private repository support
- [ ] Authentication and organizations
- [ ] Repository indexing jobs
- [ ] Developer-facing interface
- [ ] Evaluation benchmarks
- [ ] Production observability

---

## Next Milestone

The next major technical milestone is **incremental repository indexing**.

CodeNerva already stores SHA-256 content hashes for discovered source files and models repositories through snapshots.

The next step is to use those properties to determine which files actually changed between snapshots.

Instead of:

```text
New commit
    │
    ▼
Reanalyze every file
    │
    ▼
Re-embed every symbol
```

the intended flow is:

```text
New commit
    │
    ▼
Compare file hashes
    │
    ├── Unchanged ──► Reuse existing intelligence
    │
    ├── Modified ───► Reanalyze + reindex
    │
    ├── Added ──────► Analyze + index
    │
    └── Deleted ────► Remove / invalidate
```

This will reduce indexing time, embedding cost, and unnecessary processing when repositories evolve between commits.

---

## Development Philosophy

CodeNerva is being developed incrementally with tests around domain and application behavior.

The project intentionally separates:

```text
code intelligence
        from
LLM intelligence
```

The objective is not to rely on an LLM to discover an entire repository from scratch.

Instead, CodeNerva builds a structured representation of the software and provides the model with carefully retrieved evidence required to answer each question.

The system is also designed so infrastructure choices remain replaceable.

For example:

```text
Domain / Application
        │
        ├── ProjectRepository
        ├── SnapshotStore
        ├── SourceFileStore
        ├── SymbolStore
        ├── ChunkStore
        ├── VectorStore
        ├── EmbeddingProvider
        └── LLMProvider
                │
                ▼
       Infrastructure implementations
```

This makes it possible to evolve persistence, retrieval, embedding, and LLM infrastructure without rewriting the core repository intelligence logic.

---

## License

MIT License