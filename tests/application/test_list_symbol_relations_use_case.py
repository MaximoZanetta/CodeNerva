from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from codenerva.application.parsing.list_symbol_relations import (
    ListSymbolRelationsUseCase,
    SourceFileNotFoundError,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
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


def test_list_symbol_relations() -> None:
    source_file_store = InMemorySourceFileStore()
    symbol_store = InMemorySymbolStore()
    relation_store = InMemorySymbolRelationStore()

    source_file = SourceFile.create(
        snapshot_id=uuid4(),
        relative_path=PurePosixPath("app.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="a" * 64,
    )

    source_file_store.save_many((source_file,))

    validate = Symbol.create(
        source_file_id=source_file.id,
        name="validate",
        qualified_name="validate",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    handle_click = Symbol.create(
        source_file_id=source_file.id,
        name="handleClick",
        qualified_name="handleClick",
        kind=SymbolKind.FUNCTION,
        start_line=5,
        end_line=8,
    )

    symbol_store.save_many(
        (
            validate,
            handle_click,
        )
    )

    relation_store.save_many(
        (
            SymbolRelation.create(
                source_symbol_id=handle_click.id,
                target_symbol_id=validate.id,
                kind=SymbolRelationKind.CALLS,
            ),
        )
    )

    use_case = ListSymbolRelationsUseCase(
        source_file_store=source_file_store,
        symbol_store=symbol_store,
        symbol_relation_store=relation_store,
    )

    result = use_case.execute(source_file.id)

    assert len(result.relations) == 1

    relation = result.relations[0]

    assert relation.kind is SymbolRelationKind.CALLS
    assert relation.source_symbol_name == "handleClick"
    assert relation.target_symbol_name == "validate"


def test_list_symbol_relations_requires_source_file() -> None:
    use_case = ListSymbolRelationsUseCase(
        source_file_store=InMemorySourceFileStore(),
        symbol_store=InMemorySymbolStore(),
        symbol_relation_store=InMemorySymbolRelationStore(),
    )

    with pytest.raises(SourceFileNotFoundError):
        use_case.execute(uuid4())
