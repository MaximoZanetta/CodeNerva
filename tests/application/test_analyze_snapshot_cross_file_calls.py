from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.parsing.analyze_snapshot import (
    AnalyzeSnapshotUseCase,
)
from codenerva.application.parsing.build_call_relations import (
    BuildCallRelationsService,
)
from codenerva.application.parsing.build_source_file_relations import (
    BuildSourceFileRelationsService,
)
from codenerva.application.parsing.build_symbol_relations import (
    BuildSymbolRelationsService,
)
from codenerva.application.parsing.call_extractor_registry import (
    CallExtractorRegistry,
)
from codenerva.application.parsing.import_extractor_registry import (
    ImportExtractorRegistry,
)
from codenerva.application.parsing.import_reference_mapper import (
    ImportReferenceMapper,
)
from codenerva.application.parsing.imported_symbol_resolver import (
    ImportedSymbolResolver,
)
from codenerva.application.parsing.local_import_resolver import (
    LocalImportResolver,
)
from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.application.parsing.symbol_extractor_registry import (
    SymbolExtractorRegistry,
)
from codenerva.application.parsing.symbol_mapper import SymbolMapper
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.snapshot import Snapshot
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol_relation import SymbolRelationKind
from codenerva.infrastructure.in_memory_import_reference_store import (
    InMemoryImportReferenceStore,
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


def test_analyze_snapshot_builds_cross_file_call(
    tmp_path,
) -> None:
    snapshot_store = InMemorySnapshotStore()
    source_file_store = InMemorySourceFileStore()
    symbol_store = InMemorySymbolStore()
    symbol_relation_store = InMemorySymbolRelationStore()
    import_reference_store = InMemoryImportReferenceStore()
    source_file_relation_store = InMemorySourceFileRelationStore()

    repository_id = uuid4()

    snapshot = Snapshot.create(
        repository_id=repository_id,
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    )

    snapshot_store.save(snapshot)

    repository_path = tmp_path / "repositories" / str(repository_id)

    repository_path.mkdir(parents=True)

    validation_path = repository_path / "validation.js"
    validation_path.write_text(
        """
export function validateUser() {
    return true;
}
""",
        encoding="utf-8",
    )

    app_path = repository_path / "App.js"
    app_path.write_text(
        """
import { validateUser } from "./validation.js";

function handleClick() {
    validateUser();
}
""",
        encoding="utf-8",
    )

    validation_file = SourceFile.create(
        snapshot_id=snapshot.id,
        relative_path=PurePosixPath("validation.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=validation_path.stat().st_size,
        content_hash="a" * 64,
    )

    app_file = SourceFile.create(
        snapshot_id=snapshot.id,
        relative_path=PurePosixPath("App.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=app_path.stat().st_size,
        content_hash="b" * 64,
    )

    # IMPORTANTE:
    # guardamos primero validation.js para que su símbolo exista
    # antes de analizar App.js.
    source_file_store.save_many(
        (
            validation_file,
            app_file,
        )
    )

    use_case = AnalyzeSnapshotUseCase(
        snapshot_store=snapshot_store,
        source_file_store=source_file_store,
        symbol_store=symbol_store,
        source_parser=SourceParser(
            parser_registry=ParserRegistry(),
        ),
        symbol_extractor_registry=SymbolExtractorRegistry(),
        symbol_mapper=SymbolMapper(),
        storage_root=tmp_path,
        symbol_relation_store=symbol_relation_store,
        build_symbol_relations_service=BuildSymbolRelationsService(),
        import_reference_store=import_reference_store,
        import_extractor_registry=ImportExtractorRegistry(),
        import_reference_mapper=ImportReferenceMapper(),
        source_file_relation_store=source_file_relation_store,
        build_source_file_relations_service=BuildSourceFileRelationsService(
            local_import_resolver=LocalImportResolver(),
        ),
        call_extractor_registry=CallExtractorRegistry(),
        build_call_relations_service=BuildCallRelationsService(
            imported_symbol_resolver=ImportedSymbolResolver(
                source_file_relation_store=source_file_relation_store,
                symbol_store=symbol_store,
            )
        ),
    )

    result = use_case.execute(snapshot.id)

    assert result.analyzed_files == 2

    app_symbols = symbol_store.list_by_source_file_id(app_file.id)

    validation_symbols = symbol_store.list_by_source_file_id(validation_file.id)

    handle_click = next(
        symbol for symbol in app_symbols if symbol.name == "handleClick"
    )

    validate_user = next(
        symbol for symbol in validation_symbols if symbol.name == "validateUser"
    )

    relations = symbol_relation_store.list_by_source_symbol_id(handle_click.id)

    call_relations = tuple(
        relation for relation in relations if relation.kind is SymbolRelationKind.CALLS
    )

    assert len(call_relations) == 1
    assert call_relations[0].target_symbol_id == validate_user.id
