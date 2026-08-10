from uuid import uuid4

import pytest

from codenerva.application.graph.graph_traversal_service import (
    GraphTraversalService,
    SymbolNotFoundError,
)
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
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


def test_walk_calls_respects_depth() -> None:
    source_file_id = uuid4()

    handle_click = Symbol.create(
        source_file_id=source_file_id,
        name="handleClick",
        qualified_name="handleClick",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=5,
    )

    handle_streaming = Symbol.create(
        source_file_id=source_file_id,
        name="handleStreamingChat",
        qualified_name="handleStreamingChat",
        kind=SymbolKind.FUNCTION,
        start_line=7,
        end_line=12,
    )

    fetch_stream = Symbol.create(
        source_file_id=source_file_id,
        name="fetchStreamData",
        qualified_name="fetchStreamData",
        kind=SymbolKind.FUNCTION,
        start_line=14,
        end_line=20,
    )

    execute_scroll = Symbol.create(
        source_file_id=source_file_id,
        name="executeScroll",
        qualified_name="executeScroll",
        kind=SymbolKind.FUNCTION,
        start_line=22,
        end_line=25,
    )

    symbol_store = InMemorySymbolStore()
    relation_store = InMemorySymbolRelationStore()

    symbol_store.save_many(
        (
            handle_click,
            handle_streaming,
            fetch_stream,
            execute_scroll,
        )
    )

    relation_store.save_many(
        (
            SymbolRelation.create(
                source_symbol_id=handle_click.id,
                target_symbol_id=handle_streaming.id,
                kind=SymbolRelationKind.CALLS,
            ),
            SymbolRelation.create(
                source_symbol_id=handle_streaming.id,
                target_symbol_id=fetch_stream.id,
                kind=SymbolRelationKind.CALLS,
            ),
            SymbolRelation.create(
                source_symbol_id=fetch_stream.id,
                target_symbol_id=execute_scroll.id,
                kind=SymbolRelationKind.CALLS,
            ),
        )
    )

    repository = InMemoryGraphRepository(
        symbol_store=symbol_store,
        symbol_relation_store=relation_store,
        source_file_store=InMemorySourceFileStore(),
        source_file_relation_store=(InMemorySourceFileRelationStore()),
    )

    service = GraphTraversalService(
        graph_repository=repository,
    )

    result = service.walk_calls(
        symbol_id=handle_click.id,
        max_depth=2,
    )

    assert result.root.id == handle_click.id

    assert len(result.nodes) == 2

    assert result.nodes[0].symbol.id == handle_streaming.id
    assert result.nodes[0].depth == 1

    assert result.nodes[1].symbol.id == fetch_stream.id
    assert result.nodes[1].depth == 2


def test_walk_calls_avoids_cycles() -> None:
    source_file_id = uuid4()

    first = Symbol.create(
        source_file_id=source_file_id,
        name="first",
        qualified_name="first",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=2,
    )

    second = Symbol.create(
        source_file_id=source_file_id,
        name="second",
        qualified_name="second",
        kind=SymbolKind.FUNCTION,
        start_line=4,
        end_line=5,
    )

    symbol_store = InMemorySymbolStore()
    relation_store = InMemorySymbolRelationStore()

    symbol_store.save_many(
        (
            first,
            second,
        )
    )

    relation_store.save_many(
        (
            SymbolRelation.create(
                source_symbol_id=first.id,
                target_symbol_id=second.id,
                kind=SymbolRelationKind.CALLS,
            ),
            SymbolRelation.create(
                source_symbol_id=second.id,
                target_symbol_id=first.id,
                kind=SymbolRelationKind.CALLS,
            ),
        )
    )

    service = GraphTraversalService(
        graph_repository=InMemoryGraphRepository(
            symbol_store=symbol_store,
            symbol_relation_store=relation_store,
            source_file_store=InMemorySourceFileStore(),
            source_file_relation_store=(InMemorySourceFileRelationStore()),
        )
    )

    result = service.walk_calls(
        symbol_id=first.id,
        max_depth=10,
    )

    assert len(result.nodes) == 1
    assert result.nodes[0].symbol.id == second.id


def test_walk_calls_requires_symbol() -> None:
    service = GraphTraversalService(
        graph_repository=InMemoryGraphRepository(
            symbol_store=InMemorySymbolStore(),
            symbol_relation_store=InMemorySymbolRelationStore(),
            source_file_store=InMemorySourceFileStore(),
            source_file_relation_store=(InMemorySourceFileRelationStore()),
        )
    )

    with pytest.raises(SymbolNotFoundError):
        service.walk_calls(
            symbol_id=uuid4(),
            max_depth=2,
        )
