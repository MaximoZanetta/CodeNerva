from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.snapshots.reuse_cross_file_relations import (
    ReuseCrossFileRelationsUseCase,
)
from codenerva.domain.programming_language import (
    ProgrammingLanguage,
)
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelation,
    SourceFileRelationKind,
)
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
)
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_symbol_relation_store import (
    InMemorySymbolRelationStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)


def test_reuse_cross_file_relations() -> None:
    previous_snapshot_id = uuid4()
    current_snapshot_id = uuid4()

    previous_service = SourceFile.create(
        snapshot_id=previous_snapshot_id,
        relative_path=PurePosixPath("src/service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    previous_utils = SourceFile.create(
        snapshot_id=previous_snapshot_id,
        relative_path=PurePosixPath("src/utils.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="b" * 64,
    )

    current_service = SourceFile.create(
        snapshot_id=current_snapshot_id,
        relative_path=PurePosixPath("src/service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    current_utils = SourceFile.create(
        snapshot_id=current_snapshot_id,
        relative_path=PurePosixPath("src/utils.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="b" * 64,
    )

    previous_process = Symbol.create(
        source_file_id=previous_service.id,
        name="process",
        qualified_name="process",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    previous_validate = Symbol.create(
        source_file_id=previous_utils.id,
        name="validate",
        qualified_name="validate",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    current_process = Symbol.create(
        source_file_id=current_service.id,
        name="process",
        qualified_name="process",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    current_validate = Symbol.create(
        source_file_id=current_utils.id,
        name="validate",
        qualified_name="validate",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    symbol_store = InMemorySymbolStore()

    symbol_store.save_many(
        (
            previous_process,
            previous_validate,
            current_process,
            current_validate,
        )
    )

    symbol_relation_store = InMemorySymbolRelationStore()

    previous_call = SymbolRelation.create(
        source_symbol_id=previous_process.id,
        target_symbol_id=previous_validate.id,
        kind=SymbolRelationKind.CALLS,
    )

    symbol_relation_store.save_many((previous_call,))

    source_file_relation_store = InMemorySourceFileRelationStore()

    previous_import = SourceFileRelation.create(
        source_file_id=previous_service.id,
        target_file_id=previous_utils.id,
        kind=SourceFileRelationKind.IMPORTS,
    )

    source_file_relation_store.save_many((previous_import,))

    result = ReuseCrossFileRelationsUseCase(
        symbol_store=symbol_store,
        symbol_relation_store=(symbol_relation_store),
        source_file_relation_store=(source_file_relation_store),
    ).execute(
        file_pairs=(
            (
                previous_service,
                current_service,
            ),
            (
                previous_utils,
                current_utils,
            ),
        )
    )

    assert result.reused_source_file_relations == 1

    assert result.reused_symbol_relations == 1

    current_file_relations = source_file_relation_store.list_by_source_file_id(
        current_service.id
    )

    assert len(current_file_relations) == 1

    current_file_relation = current_file_relations[0]

    assert current_file_relation.target_file_id == current_utils.id

    assert current_file_relation.kind == SourceFileRelationKind.IMPORTS

    current_symbol_relations = symbol_relation_store.list_by_source_symbol_id(
        current_process.id
    )

    assert len(current_symbol_relations) == 1

    current_symbol_relation = current_symbol_relations[0]

    assert current_symbol_relation.target_symbol_id == current_validate.id

    assert current_symbol_relation.kind == SymbolRelationKind.CALLS
