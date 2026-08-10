from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.parsing.build_call_relations import (
    BuildCallRelationsService,
)
from codenerva.application.parsing.imported_symbol_resolver import (
    ImportedSymbolResolver,
)
from codenerva.application.parsing.javascript_call_extractor import (
    ExtractedCall,
)
from codenerva.domain.import_reference import ImportReference
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelation,
    SourceFileRelationKind,
)
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.domain.symbol_relation import SymbolRelationKind
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)


def test_build_call_relation_to_imported_symbol() -> None:
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

    handle_click = Symbol.create(
        source_file_id=app_file.id,
        name="handleClick",
        qualified_name="handleClick",
        kind=SymbolKind.FUNCTION,
        start_line=3,
        end_line=5,
    )

    validate_user = Symbol.create(
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

    source_file_relation_store = InMemorySourceFileRelationStore()

    symbol_store = InMemorySymbolStore()

    source_file_relation_store.save_many(
        (
            SourceFileRelation.create(
                source_file_id=app_file.id,
                target_file_id=validation_file.id,
                kind=SourceFileRelationKind.IMPORTS,
            ),
        )
    )

    symbol_store.save_many(
        (
            handle_click,
            validate_user,
        )
    )

    service = BuildCallRelationsService(
        imported_symbol_resolver=ImportedSymbolResolver(
            source_file_relation_store=source_file_relation_store,
            symbol_store=symbol_store,
        )
    )

    relations = service.build(
        calls=(
            ExtractedCall(
                caller_name="handleClick",
                callee_name="validateUser",
                line=4,
            ),
        ),
        symbols=(handle_click,),
        import_references=(import_reference,),
    )

    assert len(relations) == 1

    relation = relations[0]

    assert relation.kind is SymbolRelationKind.CALLS
    assert relation.source_symbol_id == handle_click.id
    assert relation.target_symbol_id == validate_user.id
