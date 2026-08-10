from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.parsing.imported_symbol_resolver import (
    ImportedSymbolResolver,
)
from codenerva.domain.import_reference import ImportReference
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelation,
    SourceFileRelationKind,
)
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)


def test_resolve_imported_symbol() -> None:
    snapshot_id = uuid4()

    app_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/App.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="a" * 64,
    )

    validation_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/validation.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="b" * 64,
    )

    validate_symbol = Symbol.create(
        source_file_id=validation_file.id,
        name="validateUser",
        qualified_name="validateUser",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    import_reference = ImportReference.create(
        source_file_id=app_file.id,
        module="./validation.js",
        imported_name="validateUser",
        alias=None,
        line=1,
    )

    relation_store = InMemorySourceFileRelationStore()
    symbol_store = InMemorySymbolStore()

    relation_store.save_many(
        (
            SourceFileRelation.create(
                source_file_id=app_file.id,
                target_file_id=validation_file.id,
                kind=SourceFileRelationKind.IMPORTS,
            ),
        )
    )

    symbol_store.save_many((validate_symbol,))

    resolver = ImportedSymbolResolver(
        source_file_relation_store=relation_store,
        symbol_store=symbol_store,
    )

    result = resolver.resolve(
        import_reference=import_reference,
        callee_name="validateUser",
    )

    assert result is not None
    assert result.id == validate_symbol.id
