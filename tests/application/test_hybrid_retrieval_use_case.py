from uuid import uuid4

from codenerva.application.graph.graph_query_service import (
    GraphQueryService,
)
from codenerva.application.retrieval.hybrid_retrieval import (
    HybridRetrievalUseCase,
)
from codenerva.application.retrieval.semantic_search import (
    SemanticSearchUseCase,
)
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
)
from codenerva.domain.vector_record import VectorRecord
from codenerva.infrastructure.deterministic_embedding_provider import (
    DeterministicEmbeddingProvider,
)
from codenerva.infrastructure.in_memory_graph_repository import (
    InMemoryGraphRepository,
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
from codenerva.infrastructure.in_memory_vector_store import (
    InMemoryVectorStore,
)


def test_hybrid_retrieval_expands_semantic_hit_with_graph() -> None:
    source_file_id = uuid4()
    snapshot_id = uuid4()

    validation_check = Symbol.create(
        source_file_id=source_file_id,
        name="validationCheck",
        qualified_name="validationCheck",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    handle_click = Symbol.create(
        source_file_id=source_file_id,
        name="handleClick",
        qualified_name="handleClick",
        kind=SymbolKind.FUNCTION,
        start_line=5,
        end_line=10,
    )

    handle_streaming = Symbol.create(
        source_file_id=source_file_id,
        name="handleStreamingChat",
        qualified_name="handleStreamingChat",
        kind=SymbolKind.FUNCTION,
        start_line=12,
        end_line=20,
    )

    symbol_store = InMemorySymbolStore()
    relation_store = InMemorySymbolRelationStore()

    symbol_store.save_many(
        (
            validation_check,
            handle_click,
            handle_streaming,
        )
    )

    relation_store.save_many(
        (
            SymbolRelation.create(
                source_symbol_id=handle_click.id,
                target_symbol_id=validation_check.id,
                kind=SymbolRelationKind.CALLS,
            ),
            SymbolRelation.create(
                source_symbol_id=handle_click.id,
                target_symbol_id=handle_streaming.id,
                kind=SymbolRelationKind.CALLS,
            ),
        )
    )

    graph_repository = InMemoryGraphRepository(
        symbol_store=symbol_store,
        symbol_relation_store=relation_store,
        source_file_store=InMemorySourceFileStore(),
        source_file_relation_store=(InMemorySourceFileRelationStore()),
    )

    embedding_provider = DeterministicEmbeddingProvider(
        dimensions=8,
    )

    vector_store = InMemoryVectorStore()

    query = "validate user input"

    query_vector = embedding_provider.embed((query,))[0]

    vector_store.save_many(
        (
            VectorRecord(
                chunk_id=uuid4(),
                vector=query_vector,
                snapshot_id=snapshot_id,
                source_file_id=source_file_id,
                symbol_id=validation_check.id,
                relative_path="App.js",
                language="javascript",
                qualified_name="validationCheck",
                symbol_kind="FUNCTION",
            ),
        )
    )

    semantic_search = SemanticSearchUseCase(
        embedding_provider=embedding_provider,
        vector_store=vector_store,
    )

    graph_query_service = GraphQueryService(
        graph_repository=graph_repository,
    )

    use_case = HybridRetrievalUseCase(
        semantic_search=semantic_search,
        graph_query_service=graph_query_service,
    )

    result = use_case.execute(
        snapshot_id=snapshot_id,
        query=query,
        top_k=1,
    )

    assert len(result.semantic_hits) == 1

    assert result.semantic_hits[0].symbol.id == validation_check.id

    assert result.semantic_hits[0].score == 1.0

    called_by = tuple(
        item for item in result.expanded_symbols if item.relation == "CALLED_BY"
    )

    assert len(called_by) == 1
    assert called_by[0].symbol.id == handle_click.id
