from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.parsing.build_call_relations import (
    BuildCallRelationsService,
)
from codenerva.application.parsing.extracted_call import ExtractedCall
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
from codenerva.domain.symbol_relation import SymbolRelationKind
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)


def test_build_call_relation() -> None:
    source_file_id = uuid4()

    validate = Symbol.create(
        source_file_id=source_file_id,
        name="validate",
        qualified_name="validate",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=2,
    )

    process = Symbol.create(
        source_file_id=source_file_id,
        name="process",
        qualified_name="process",
        kind=SymbolKind.FUNCTION,
        start_line=4,
        end_line=5,
    )

    service = BuildCallRelationsService(
        imported_symbol_resolver=ImportedSymbolResolver(
            source_file_relation_store=InMemorySourceFileRelationStore(),
            symbol_store=InMemorySymbolStore(),
        )
    )

    relations = service.build(
        calls=(
            ExtractedCall(
                caller_name="process",
                callee_name="validate",
                line=5,
            ),
        ),
        symbols=(
            validate,
            process,
        ),
        import_references=(),
    )

    assert len(relations) == 1
    assert relations[0].source_symbol_id == process.id
    assert relations[0].target_symbol_id == validate.id
    assert relations[0].kind is SymbolRelationKind.CALLS


def test_build_call_relation_to_imported_method() -> None:
    snapshot_id = uuid4()

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

    post_fizz = Symbol.create(
        source_file_id=controller_file.id,
        name="post_fizz",
        qualified_name="post_fizz",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=4,
    )

    fizz_service = Symbol.create(
        source_file_id=service_file.id,
        name="FizzService",
        qualified_name="FizzService",
        kind=SymbolKind.CLASS,
        start_line=1,
        end_line=20,
    )

    create = Symbol.create(
        source_file_id=service_file.id,
        name="create",
        qualified_name="FizzService.create",
        kind=SymbolKind.METHOD,
        start_line=10,
        end_line=15,
        parent_symbol_id=fizz_service.id,
    )

    import_reference = ImportReference.create(
        source_file_id=controller_file.id,
        module="app.fizz.service",
        imported_name="FizzService",
        alias=None,
        line=1,
    )

    source_file_relation_store = InMemorySourceFileRelationStore()
    symbol_store = InMemorySymbolStore()

    source_file_relation_store.save_many(
        (
            SourceFileRelation.create(
                source_file_id=controller_file.id,
                target_file_id=service_file.id,
                kind=SourceFileRelationKind.IMPORTS,
            ),
        )
    )

    symbol_store.save_many(
        (
            post_fizz,
            fizz_service,
            create,
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
                caller_name="post_fizz",
                callee_name="create",
                owner_name="FizzService",
                line=3,
            ),
        ),
        symbols=(post_fizz,),
        import_references=(import_reference,),
    )

    assert len(relations) == 1

    relation = relations[0]

    assert relation.source_symbol_id == post_fizz.id
    assert relation.target_symbol_id == create.id
    assert relation.kind == SymbolRelationKind.CALLS
