from uuid import uuid4

import pytest

from codenerva.application.graph.graph_query_service import (
    GraphQueryService,
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


def test_get_symbol_neighbors() -> None:
    source_file_id = uuid4()

    handle_click = Symbol.create(
        source_file_id=source_file_id,
        name="handleClick",
        qualified_name="handleClick",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=5,
    )

    validate = Symbol.create(
        source_file_id=source_file_id,
        name="validate",
        qualified_name="validate",
        kind=SymbolKind.FUNCTION,
        start_line=7,
        end_line=9,
    )

    process = Symbol.create(
        source_file_id=source_file_id,
        name="process",
        qualified_name="process",
        kind=SymbolKind.FUNCTION,
        start_line=11,
        end_line=15,
    )

    symbol_store = InMemorySymbolStore()
    relation_store = InMemorySymbolRelationStore()

    symbol_store.save_many(
        (
            handle_click,
            validate,
            process,
        )
    )

    relation_store.save_many(
        (
            SymbolRelation.create(
                source_symbol_id=handle_click.id,
                target_symbol_id=validate.id,
                kind=SymbolRelationKind.CALLS,
            ),
            SymbolRelation.create(
                source_symbol_id=process.id,
                target_symbol_id=handle_click.id,
                kind=SymbolRelationKind.CALLS,
            ),
        )
    )

    graph_repository = InMemoryGraphRepository(
        symbol_store=symbol_store,
        symbol_relation_store=relation_store,
        source_file_store=InMemorySourceFileStore(),
        source_file_relation_store=InMemorySourceFileRelationStore(),
    )

    service = GraphQueryService(
        graph_repository=graph_repository,
    )

    result = service.get_symbol_neighbors(handle_click.id)

    assert result.symbol.id == handle_click.id

    assert len(result.calls) == 1
    assert result.calls[0].id == validate.id

    assert len(result.called_by) == 1
    assert result.called_by[0].id == process.id

    assert result.contains == ()


def test_get_symbol_neighbors_requires_symbol() -> None:
    symbol_store = InMemorySymbolStore()
    relation_store = InMemorySymbolRelationStore()

    service = GraphQueryService(
        graph_repository=InMemoryGraphRepository(
            symbol_store=symbol_store,
            symbol_relation_store=relation_store,
            source_file_store=InMemorySourceFileStore(),
            source_file_relation_store=InMemorySourceFileRelationStore(),
        )
    )

    with pytest.raises(SymbolNotFoundError):
        service.get_symbol_neighbors(uuid4())
