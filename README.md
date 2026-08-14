# CodeNerva

> AI-native code intelligence platform for understanding, indexing, and querying software repositories.

CodeNerva transforms source code repositories into structured, persistent knowledge that can be explored by developers and AI systems.

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

CodeNerva goes further by combining semantic similarity with structural relationships extracted directly from source code.

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
                 ┌─────┴─────┐
                 │           │
                 ▼           ▼
          Semantic Search  Graph Expansion
                 │           │
                 └─────┬─────┘
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

The LLM is not expected to discover the repository structure by itself. CodeNerva builds that structure before asking the model to reason over relevant evidence.

---

## Backend V1 Status

**Backend V1 is complete.**

The V1 backend implements an end-to-end repository intelligence pipeline: repository ingestion, static analysis, persistent indexing, hybrid retrieval, repository-grounded question answering, analysis jobs, and a REST API prepared for the frontend.

CodeNerva remains a development-stage project and is not yet intended for production repository workloads.

### Repository ingestion

- ✅ Project registration and retrieval
- ✅ GitHub repository registration
- ✅ Git repository validation
- ✅ Repository cloning
- ✅ Commit-based repository snapshots
- ✅ Source file discovery
- ✅ SHA-256 content hashing
- ✅ Programming language detection
- ✅ Repository-wide analysis

### Static code analysis

- ✅ Tree-sitter parsing
- ✅ Multi-language parsing architecture
- ✅ Symbol extraction
- ✅ Functions, classes, methods, and nested symbols
- ✅ Qualified symbol names
- ✅ Import extraction
- ✅ Local import resolution
- ✅ TypeScript path alias resolution
- ✅ Cross-file relationships
- ✅ Function call extraction
- ✅ Cross-file call resolution
- ✅ `CALLS` / `CALLED_BY` graph traversal
- ✅ `CONTAINS` relationships

### Indexing and retrieval

- ✅ Symbol-aware code chunking
- ✅ OpenAI embedding generation
- ✅ Qdrant vector storage
- ✅ Snapshot-scoped semantic search
- ✅ Knowledge-graph expansion
- ✅ Hybrid retrieval
- ✅ Hybrid reranking
- ✅ Context deduplication
- ✅ Context budgeting
- ✅ Retrieval diagnostics
- ✅ Incremental snapshot indexing
- ✅ Reuse of unchanged repository intelligence

### Repository QA

- ✅ Repository-wide question answering
- ✅ Retrieval context generation
- ✅ LLM-based answers
- ✅ Multi-file reasoning
- ✅ Cross-language flow explanation
- ✅ Snapshot-scoped questions
- ✅ Grounded source metadata
- ✅ Protection against questions on snapshots that are not ready

### Persistence and lifecycle

- ✅ PostgreSQL persistence
- ✅ SQLAlchemy persistence layer
- ✅ Alembic database migrations
- ✅ Persistent projects
- ✅ Persistent repositories
- ✅ Persistent snapshots
- ✅ Persistent source files
- ✅ Persistent symbols
- ✅ Persistent import references
- ✅ Persistent source-file relationships
- ✅ Persistent symbol relationships
- ✅ Persistent chunks
- ✅ Persistent analysis jobs
- ✅ Qdrant vector persistence
- ✅ Repository QA across API restarts
- ✅ Snapshot lifecycle
- ✅ Analysis job lifecycle and progress

### API and quality

- ✅ FastAPI REST API
- ✅ Project read/write endpoints
- ✅ Repository read/write endpoints
- ✅ Snapshot read/write endpoints
- ✅ Analysis job endpoints
- ✅ Repository question endpoint
- ✅ CORS configuration for the frontend
- ✅ Domain, application, API, infrastructure, integration, and evaluation tests
- ✅ Ruff linting and formatting
- ✅ LLM-as-a-Judge evaluation

---

## How It Works

The V1 pipeline can be summarized as:

```text
Project
   │
   ▼
Repository
   │
   ▼
Clone
   │
   ▼
Snapshot
   │
   ▼
Analysis Job
   │
   ├── Discover files
   │
   └── Process repository
          │
          ├── Parse source code
          ├── Extract symbols
          ├── Extract imports
          ├── Resolve relationships
          ├── Build call graph
          ├── Chunk symbols
          ├── Generate embeddings
          └── Index vectors
                 │
                 ▼
               READY
                 │
                 ▼
             Question
                 │
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
        Grounded Answer + Sources
```

Once repository intelligence is persisted, CodeNerva can answer questions after an application restart without rebuilding the entire representation.

---

## Architecture

CodeNerva follows a layered Clean Architecture.

```text
                    API
                     │
                     ▼
               Application
                     │
                     ▼
                  Domain
                     ▲
                     │
              Infrastructure
              ├── PostgreSQL
              ├── Qdrant
              ├── Git
              ├── Tree-sitter
              └── OpenAI
```

The project is built around explicit boundaries between domain concepts and infrastructure.

Main principles:

- Clean Architecture
- Dependency Inversion
- Domain-Driven Design foundations
- Explicit application use cases
- Repository / Store abstractions
- Infrastructure-independent domain models
- Testability
- Deterministic IDs where appropriate
- Replaceable external providers
- Persistent repository intelligence

External systems such as embedding providers, vector databases, relational databases, Git, and LLM providers are accessed behind application/domain abstractions where appropriate.

---

## Repository Intelligence

CodeNerva separates repository intelligence into structured and semantic representations.

### Structured knowledge

Static analysis produces entities such as:

```text
Repository
└── Snapshot
    └── Source Files
        ├── Symbols
        ├── Imports
        ├── File Relations
        └── Symbol Relations
```

Examples of structural relationships include:

```text
CONTAINS
IMPORTS
CALLS
CALLED_BY
```

This representation allows CodeNerva to reason about code relationships that pure vector search cannot reliably reconstruct.

### Semantic knowledge

Source symbols are converted into chunks containing metadata such as:

```text
Snapshot
File
Language
Qualified symbol name
Symbol kind
Line range
Source code
```

Embeddings for those chunks are stored in Qdrant and filtered by `snapshot_id` during semantic search.

---

## Hybrid Retrieval

CodeNerva combines semantic and graph retrieval.

```text
Question
   │
   ▼
Query Embedding
   │
   ▼
Snapshot-scoped
Qdrant Search
   │
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
   ├── Deduplication
   └── Character / item budget
   │
   ▼
Prompt
   │
   ▼
LLM
   │
   ▼
Answer + Sources + Retrieval Diagnostics
```

Semantic retrieval identifies code related to the natural-language question.

Graph expansion then adds structurally relevant symbols such as callers and callees, even when those symbols are not themselves strong semantic matches.

The combined candidates are reranked before the final context is assembled.

---

## Snapshot Isolation

Repositories are represented through commit-based snapshots.

Every semantic query is scoped by `snapshot_id`:

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

This prevents vectors from different repository versions from being mixed during retrieval.

A snapshot also has a lifecycle. Repository questions are accepted only after the snapshot is ready, preventing incomplete repository intelligence from being queried as though analysis had finished.

---

## Analysis Jobs

Repository analysis is represented explicitly as an analysis job.

A job moves through the V1 lifecycle and exposes progress to API clients.

Conceptually:

```text
QUEUED
   │
   ▼
DISCOVERING
   │
   ▼
PROCESSING
   │
   ▼
READY
```

If a pipeline stage fails:

```text
QUEUED / DISCOVERING / PROCESSING
               │
               ▼
             FAILED
```

Analysis jobs are persisted in PostgreSQL, allowing their state to survive application restarts.

The V1 orchestration is intentionally simpler than a production distributed worker system. Moving long-running processing to a dedicated job queue/worker is a V2 concern.

---

## Incremental Indexing

CodeNerva uses snapshot comparison and source-file content hashes to avoid unnecessarily rebuilding unchanged repository intelligence.

```text
Previous Snapshot
       │
       │ compare paths + hashes
       ▼
Current Snapshot
       │
       ├── Unchanged ──► Reuse intelligence
       ├── Modified ───► Analyze + reindex
       ├── Added ──────► Analyze + index
       └── Deleted ────► Exclude from current snapshot
```

For unchanged files, CodeNerva can reuse persisted symbols, relationships, chunks, and vectors where applicable.

This reduces repeated parsing, indexing work, and embedding cost as repositories evolve.

---

## Persistence

CodeNerva persists structured repository intelligence in PostgreSQL.

```text
PostgreSQL
├── Projects
├── Repositories
├── Snapshots
├── Analysis Jobs
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

The two representations are connected through stable identifiers and snapshot metadata.

```text
PostgreSQL                 Qdrant
     │                        │
Structured Knowledge      Embeddings
     │                        │
     └──────────┬─────────────┘
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

---

## Evaluation

V1 includes automated evaluation in addition to conventional unit and integration tests.

Evaluation covers repository questions using known expected facts and repository context.

The evaluation system includes:

- Repository evaluation fixtures
- Retrieval diagnostics
- Expected-fact evaluation
- LLM-as-a-Judge scoring
- Correctness scoring
- Groundedness scoring
- Completeness scoring

Example judge output:

```text
Correctness:   1.000
Groundedness:  1.000
Completeness:  1.000
Mean score:    1.000
```

LLM-based evaluation is inherently less deterministic than conventional tests. A single judge-score fluctuation should therefore be investigated before being treated as a deterministic application regression.

---

## API

The REST API exposes the core V1 workflow.

Representative endpoints include:

```text
GET    /health

POST   /api/v1/projects
GET    /api/v1/projects
GET    /api/v1/projects/{project_id}

POST   /api/v1/projects/{project_id}/repository
GET    /api/v1/projects/{project_id}/repository

POST   /api/v1/repositories/{repository_id}/clone
POST   /api/v1/repositories/{repository_id}/snapshots
GET    /api/v1/repositories/{repository_id}/snapshots

GET    /api/v1/snapshots/{snapshot_id}

POST   /api/v1/analysis-jobs
GET    /api/v1/analysis-jobs/{job_id}

POST   /api/v1/questions
```

The exact OpenAPI contract can be inspected through FastAPI's generated documentation while the application is running.

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
- Alembic
- Qdrant

### Testing

- pytest
- httpx
- Deterministic test embedding provider
- In-memory infrastructure implementations
- Integration tests
- Evaluation fixtures
- LLM-as-a-Judge

### Code Quality

- Ruff

### Frontend

Frontend development begins after the Backend V1 milestone.

### Planned Infrastructure

- Docker
- Dedicated background worker / job queue
- Production observability
- CI/CD

---

## Project Structure

```text
src/
└── codenerva/
    ├── api/
    ├── application/
    │   ├── analysis/
    │   ├── chunking/
    │   ├── embeddings/
    │   ├── parsing/
    │   ├── qa/
    │   ├── repository/
    │   ├── retrieval/
    │   ├── snapshots/
    │   └── source/
    ├── domain/
    └── infrastructure/
        └── database/

tests/
├── api/
├── application/
├── domain/
├── evaluation/
├── infrastructure/
└── integration/

scripts/

storage/
├── repositories/
└── qdrant/

alembic/
└── versions/
```

---

## Running Locally

### 1. Clone the repository

```bash
git clone <repository-url>
cd CodeNerva
```

### 2. Install dependencies

```bash
uv sync
```

### 3. Configure environment variables

PostgreSQL:

```text
DATABASE_URL=postgresql+psycopg://<user>:<password>@localhost:5432/codenerva
```

OpenAI-backed embeddings, repository QA, and LLM evaluation:

```text
OPENAI_API_KEY=your-api-key
```

Do not commit credentials or local environment files containing secrets.

### 4. Apply database migrations

```bash
uv run alembic upgrade head
```

### 5. Run the API

```bash
uv run uvicorn codenerva.main:app --reload
```

Swagger UI is available at:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
GET /health
```

---

## Testing

Run the complete test suite:

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

Some evaluation tests call external LLM services and therefore require `OPENAI_API_KEY`. LLM-as-a-Judge results may exhibit limited run-to-run variance.

---

## V1 Scope

Backend V1 establishes the core repository-intelligence architecture.

It includes:

- Repository ingestion
- Commit-based snapshots
- Static multi-language code analysis
- Persistent repository knowledge
- Knowledge-graph relationships
- Symbol-aware chunking
- Embeddings and vector indexing
- Hybrid semantic + graph retrieval
- Context construction and budgeting
- Repository-grounded LLM answers
- Sources and retrieval diagnostics
- Incremental indexing
- Persistent analysis jobs
- Snapshot readiness lifecycle
- REST API
- Automated evaluation

The purpose of V1 is not to solve every code-intelligence problem. It establishes a working, testable architecture on which more advanced intelligence and product capabilities can be built.

---

## Next Milestone — Frontend V1

With Backend V1 complete, the next milestone is a developer-facing interface.

The initial frontend flow is intended to expose the existing backend capabilities:

```text
Projects
   │
   ▼
Repository
   │
   ▼
Snapshots
   │
   ▼
Analysis Status
   │
   ▼
Repository Chat
   │
   ▼
Answer + Sources
```

The frontend should make it possible to register a repository, analyze a snapshot, observe analysis progress, ask repository questions, and inspect the source evidence used to produce an answer.

---

## Backend V2 Roadmap

V2 will focus on making repository intelligence more conversational, resilient, scalable, and precise.

### Conversational intelligence

- [ ] Persistent conversations and messages
- [ ] Conversation history by project/snapshot
- [ ] Conversational RAG
- [ ] Query rewriting from conversation context
- [ ] Intelligent selection of previous messages
- [ ] Persist sources and diagnostics with answers

### Processing and reliability

- [ ] Dedicated background worker / job queue
- [ ] Retry policies
- [ ] Job cancellation
- [ ] More granular analysis progress
- [ ] Stronger idempotency and concurrency control
- [ ] Structured pipeline failure information

### Retrieval

- [ ] Lexical / BM25 retrieval
- [ ] Retrieval fusion such as RRF
- [ ] More advanced reranking
- [ ] Multi-query retrieval
- [ ] Dynamic retrieval depth
- [ ] Multi-hop graph traversal
- [ ] Question-aware graph expansion
- [ ] Agentic / tool-driven repository investigation

### Code intelligence

- [ ] Architecture-level repository analysis
- [ ] Entrypoint detection
- [ ] Module and subsystem discovery
- [ ] Additional graph relation types
- [ ] Improved cross-file call resolution
- [ ] Change-impact analysis
- [ ] Test-to-production-code relationships
- [ ] Repository-level summaries
- [ ] Deeper multi-language support

### GitHub and product capabilities

- [ ] GitHub OAuth
- [ ] Private repository support
- [ ] GitHub webhooks
- [ ] Automatic snapshots on new commits
- [ ] Authentication
- [ ] Users and organizations
- [ ] Project permissions

### Production infrastructure

- [ ] Docker
- [ ] Rate limiting
- [ ] Usage and cost tracking
- [ ] Structured logging
- [ ] Metrics and tracing
- [ ] Managed PostgreSQL / Qdrant deployment
- [ ] CI/CD
- [ ] Resource cleanup and retention policies
- [ ] Security hardening for untrusted repositories

### Evaluation

- [ ] Larger multi-repository benchmark
- [ ] More languages in the evaluation corpus
- [ ] Architecture and debugging question sets
- [ ] Retrieval regression benchmarks
- [ ] More deterministic fact-level evaluation
- [ ] Improved LLM-judge stability

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

One of CodeNerva's primary product directions is developer onboarding into large, unfamiliar codebases.

Potential applications include:

- Repository onboarding
- Architecture exploration
- Execution-flow tracing
- Dependency analysis
- Change-impact analysis
- AI-assisted codebase navigation
- Engineering knowledge discovery

---

## Development Philosophy

CodeNerva intentionally separates:

```text
code intelligence
        from
LLM intelligence
```

The objective is not to rely on an LLM to discover an entire repository from scratch.

Instead, CodeNerva builds a structured representation of the software and provides the model with carefully retrieved evidence required to answer each question.

Infrastructure choices are designed to remain replaceable:

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

This allows persistence, retrieval, embedding, and LLM infrastructure to evolve without rewriting the core repository-intelligence logic.

---

## License

MIT License
