from dataclasses import dataclass
from pathlib import PurePosixPath
from uuid import UUID, uuid4

from codenerva.application.graph.graph_query_service import (
    GraphQueryService,
)
from codenerva.application.retrieval.hybrid_reranker import (
    HybridReranker,
)
from codenerva.application.retrieval.hybrid_retrieval import (
    HybridRetrievalUseCase,
)
from codenerva.application.retrieval.retrieval_context_builder import (
    RetrievalContextBuilder,
)
from codenerva.application.retrieval.semantic_search import (
    SemanticSearchResult,
)
from codenerva.domain.chunk import Chunk
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.snapshot import Snapshot
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
)
from codenerva.domain.vector_record import VectorRecord
from codenerva.domain.vector_search_result import VectorSearchResult
from codenerva.infrastructure.in_memory_chunk_store import (
    InMemoryChunkStore,
)
from codenerva.infrastructure.in_memory_graph_repository import (
    InMemoryGraphRepository,
)
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)
from codenerva.infrastructure.in_memory_symbol_relation_store import (
    InMemorySymbolRelationStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)
from tests.evaluation.fakes import (
    FakeSemanticSearchUseCase,
)

END_TO_END_QUESTION = (
    "How does the fizz feature work from the API route "
    "through the service and model layers?"
)

STRUCTURE_QUESTION = "What methods belong to FizzService?"

TESTING_QUESTION = "How is the Fizz model tested?"
INSUFFICIENT_CONTEXT_QUESTION = (
    "What authentication mechanism protects the fizz API "
    "and how are access tokens validated?"
)

PARTIAL_EVIDENCE_QUESTION = (
    "How is a Fizz created and what happens if the database commit fails?"
)


@dataclass(frozen=True, slots=True)
class FizzEvaluationFixture:
    snapshot_id: UUID
    snapshot_store: InMemorySnapshotStore
    hybrid_retrieval: HybridRetrievalUseCase
    hybrid_reranker: HybridReranker
    context_builder: RetrievalContextBuilder


def build_fizz_evaluation_fixture() -> FizzEvaluationFixture:
    snapshot = Snapshot.create(
        repository_id=uuid4(),
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/fizz",
    ).mark_ready()

    snapshot_id = snapshot.id

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)
    controller_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/fizz/controller.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    service_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/fizz/service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="b" * 64,
    )

    model_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/fizz/model.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="c" * 64,
    )

    schema_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/fizz/schema.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="d" * 64,
    )

    test_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/fizz/model_test.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="e" * 64,
    )

    source_file_store = InMemorySourceFileStore()

    source_file_store.save_many(
        (
            controller_file,
            service_file,
            model_file,
            schema_file,
            test_file,
        )
    )

    post_fizz = Symbol.create(
        source_file_id=controller_file.id,
        name="post_fizz",
        qualified_name="post_fizz",
        kind=SymbolKind.FUNCTION,
        start_line=22,
        end_line=26,
    )

    get_fizz = Symbol.create(
        source_file_id=controller_file.id,
        name="get_fizz",
        qualified_name="get_fizz",
        kind=SymbolKind.FUNCTION,
        start_line=14,
        end_line=16,
    )

    fizz_service = Symbol.create(
        source_file_id=service_file.id,
        name="FizzService",
        qualified_name="FizzService",
        kind=SymbolKind.CLASS,
        start_line=10,
        end_line=44,
    )

    create = Symbol.create(
        source_file_id=service_file.id,
        name="create",
        qualified_name="FizzService.create",
        kind=SymbolKind.METHOD,
        start_line=38,
        end_line=44,
        parent_symbol_id=fizz_service.id,
    )

    get_all = Symbol.create(
        source_file_id=service_file.id,
        name="get_all",
        qualified_name="FizzService.get_all",
        kind=SymbolKind.METHOD,
        start_line=12,
        end_line=14,
        parent_symbol_id=fizz_service.id,
    )

    fizz_model = Symbol.create(
        source_file_id=model_file.id,
        name="Fizz",
        qualified_name="Fizz",
        kind=SymbolKind.CLASS,
        start_line=7,
        end_line=19,
    )

    fizz_schema = Symbol.create(
        source_file_id=schema_file.id,
        name="FizzSchema",
        qualified_name="FizzSchema",
        kind=SymbolKind.CLASS,
        start_line=6,
        end_line=11,
    )

    test_fizz = Symbol.create(
        source_file_id=test_file.id,
        name="fizz",
        qualified_name="fizz",
        kind=SymbolKind.FUNCTION,
        start_line=9,
        end_line=11,
    )

    symbol_store = InMemorySymbolStore()

    symbol_store.save_many(
        (
            post_fizz,
            get_fizz,
            fizz_service,
            create,
            get_all,
            fizz_model,
            fizz_schema,
            test_fizz,
        )
    )

    symbol_relation_store = InMemorySymbolRelationStore()

    symbol_relation_store.save_many(
        (
            SymbolRelation.create(
                source_symbol_id=fizz_service.id,
                target_symbol_id=create.id,
                kind=SymbolRelationKind.CONTAINS,
            ),
            SymbolRelation.create(
                source_symbol_id=fizz_service.id,
                target_symbol_id=get_all.id,
                kind=SymbolRelationKind.CONTAINS,
            ),
            SymbolRelation.create(
                source_symbol_id=post_fizz.id,
                target_symbol_id=create.id,
                kind=SymbolRelationKind.CALLS,
            ),
            SymbolRelation.create(
                source_symbol_id=get_fizz.id,
                target_symbol_id=get_all.id,
                kind=SymbolRelationKind.CALLS,
            ),
        )
    )

    chunk_store = InMemoryChunkStore()

    chunks = (
        Chunk.create(
            snapshot_id=snapshot_id,
            source_file_id=controller_file.id,
            symbol_id=post_fizz.id,
            text="post_fizz",
            code=(
                "async def post_fizz(fizz, session):\n"
                "    return await FizzService.create(fizz, session)"
            ),
            relative_path="app/fizz/controller.py",
            language="python",
            qualified_name="post_fizz",
            symbol_kind="FUNCTION",
            start_line=22,
            end_line=26,
        ),
        Chunk.create(
            snapshot_id=snapshot_id,
            source_file_id=controller_file.id,
            symbol_id=get_fizz.id,
            text="get_fizz",
            code=(
                "async def get_fizz(session):\n"
                "    return await FizzService.get_all(session)"
            ),
            relative_path="app/fizz/controller.py",
            language="python",
            qualified_name="get_fizz",
            symbol_kind="FUNCTION",
            start_line=14,
            end_line=16,
        ),
        Chunk.create(
            snapshot_id=snapshot_id,
            source_file_id=service_file.id,
            symbol_id=fizz_service.id,
            text="FizzService",
            code="class FizzService: pass",
            relative_path="app/fizz/service.py",
            language="python",
            qualified_name="FizzService",
            symbol_kind="CLASS",
            start_line=10,
            end_line=44,
        ),
        Chunk.create(
            snapshot_id=snapshot_id,
            source_file_id=service_file.id,
            symbol_id=create.id,
            text="FizzService.create",
            code="async def create(...): pass",
            relative_path="app/fizz/service.py",
            language="python",
            qualified_name="FizzService.create",
            symbol_kind="METHOD",
            start_line=38,
            end_line=44,
        ),
        Chunk.create(
            snapshot_id=snapshot_id,
            source_file_id=service_file.id,
            symbol_id=get_all.id,
            text="FizzService.get_all",
            code="async def get_all(...): pass",
            relative_path="app/fizz/service.py",
            language="python",
            qualified_name="FizzService.get_all",
            symbol_kind="METHOD",
            start_line=12,
            end_line=14,
        ),
        Chunk.create(
            snapshot_id=snapshot_id,
            source_file_id=model_file.id,
            symbol_id=fizz_model.id,
            text="Fizz",
            code="class Fizz(Base): pass",
            relative_path="app/fizz/model.py",
            language="python",
            qualified_name="Fizz",
            symbol_kind="CLASS",
            start_line=7,
            end_line=19,
        ),
        Chunk.create(
            snapshot_id=snapshot_id,
            source_file_id=schema_file.id,
            symbol_id=fizz_schema.id,
            text="FizzSchema",
            code="class FizzSchema(CamelModel): pass",
            relative_path="app/fizz/schema.py",
            language="python",
            qualified_name="FizzSchema",
            symbol_kind="CLASS",
            start_line=6,
            end_line=11,
        ),
        Chunk.create(
            snapshot_id=snapshot_id,
            source_file_id=test_file.id,
            symbol_id=test_fizz.id,
            text="fizz test helper",
            code="def fizz(): pass",
            relative_path="app/fizz/model_test.py",
            language="python",
            qualified_name="fizz",
            symbol_kind="FUNCTION",
            start_line=9,
            end_line=11,
        ),
    )

    chunk_store.save_many(chunks)

    end_to_end_semantic_result = SemanticSearchResult(
        results=(
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[2].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=service_file.id,
                    symbol_id=fizz_service.id,
                    relative_path="app/fizz/service.py",
                    language="python",
                    qualified_name="FizzService",
                    symbol_kind="CLASS",
                ),
                score=0.59,
            ),
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[7].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=test_file.id,
                    symbol_id=test_fizz.id,
                    relative_path="app/fizz/model_test.py",
                    language="python",
                    qualified_name="fizz",
                    symbol_kind="FUNCTION",
                ),
                score=0.58,
            ),
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[0].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=controller_file.id,
                    symbol_id=post_fizz.id,
                    relative_path="app/fizz/controller.py",
                    language="python",
                    qualified_name="post_fizz",
                    symbol_kind="FUNCTION",
                ),
                score=0.57,
            ),
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[1].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=controller_file.id,
                    symbol_id=get_fizz.id,
                    relative_path="app/fizz/controller.py",
                    language="python",
                    qualified_name="get_fizz",
                    symbol_kind="FUNCTION",
                ),
                score=0.56,
            ),
        )
    )

    structure_semantic_result = SemanticSearchResult(
        results=(
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[2].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=service_file.id,
                    symbol_id=fizz_service.id,
                    relative_path="app/fizz/service.py",
                    language="python",
                    qualified_name="FizzService",
                    symbol_kind="CLASS",
                ),
                score=0.90,
            ),
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[3].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=service_file.id,
                    symbol_id=create.id,
                    relative_path="app/fizz/service.py",
                    language="python",
                    qualified_name="FizzService.create",
                    symbol_kind="METHOD",
                ),
                score=0.85,
            ),
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[4].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=service_file.id,
                    symbol_id=get_all.id,
                    relative_path="app/fizz/service.py",
                    language="python",
                    qualified_name="FizzService.get_all",
                    symbol_kind="METHOD",
                ),
                score=0.84,
            ),
        )
    )
    insufficient_context_semantic_result = SemanticSearchResult(
        results=(
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[2].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=service_file.id,
                    symbol_id=fizz_service.id,
                    relative_path="app/fizz/service.py",
                    language="python",
                    qualified_name="FizzService",
                    symbol_kind="CLASS",
                ),
                score=0.30,
            ),
        )
    )

    partial_evidence_semantic_result = SemanticSearchResult(
        results=(
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[3].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=service_file.id,
                    symbol_id=create.id,
                    relative_path="app/fizz/service.py",
                    language="python",
                    qualified_name="FizzService.create",
                    symbol_kind="METHOD",
                ),
                score=0.90,
            ),
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[2].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=service_file.id,
                    symbol_id=fizz_service.id,
                    relative_path="app/fizz/service.py",
                    language="python",
                    qualified_name="FizzService",
                    symbol_kind="CLASS",
                ),
                score=0.70,
            ),
        )
    )

    testing_semantic_result = SemanticSearchResult(
        results=(
            VectorSearchResult(
                record=VectorRecord(
                    chunk_id=chunks[7].id,
                    vector=(1.0, 0.0),
                    snapshot_id=snapshot_id,
                    source_file_id=test_file.id,
                    symbol_id=test_fizz.id,
                    relative_path="app/fizz/model_test.py",
                    language="python",
                    qualified_name="fizz",
                    symbol_kind="FUNCTION",
                ),
                score=0.95,
            ),
        )
    )

    source_file_relation_store = InMemorySourceFileRelationStore()

    graph_repository = InMemoryGraphRepository(
        symbol_store=symbol_store,
        symbol_relation_store=symbol_relation_store,
        source_file_store=source_file_store,
        source_file_relation_store=(source_file_relation_store),
    )

    graph_query_service = GraphQueryService(
        graph_repository=graph_repository,
    )

    hybrid_retrieval = HybridRetrievalUseCase(
        semantic_search=FakeSemanticSearchUseCase(
            results_by_query={
                END_TO_END_QUESTION: (end_to_end_semantic_result),
                STRUCTURE_QUESTION: (structure_semantic_result),
                TESTING_QUESTION: (testing_semantic_result),
                INSUFFICIENT_CONTEXT_QUESTION: (insufficient_context_semantic_result),
                PARTIAL_EVIDENCE_QUESTION: (partial_evidence_semantic_result),
            }
        ),
        graph_query_service=graph_query_service,
    )

    return FizzEvaluationFixture(
        snapshot_id=snapshot_id,
        snapshot_store=snapshot_store,
        hybrid_retrieval=hybrid_retrieval,
        hybrid_reranker=HybridReranker(
            source_file_store=source_file_store,
        ),
        context_builder=RetrievalContextBuilder(
            chunk_store=chunk_store,
        ),
    )
