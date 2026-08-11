from pathlib import Path, PurePosixPath
from uuid import uuid4

from codenerva.application.parsing.analyze_source_file import (
    AnalyzeSourceFileUseCase,
)
from codenerva.application.parsing.build_call_relations import BuildCallRelationsService
from codenerva.application.parsing.build_source_file_relations import (
    BuildSourceFileRelationsService,
)
from codenerva.application.parsing.build_symbol_relations import (
    BuildSymbolRelationsService,
)
from codenerva.application.parsing.call_extractor_registry import CallExtractorRegistry
from codenerva.application.parsing.import_extractor_registry import (
    ImportExtractorRegistry,
)
from codenerva.application.parsing.import_reference_mapper import ImportReferenceMapper
from codenerva.application.parsing.imported_symbol_resolver import (
    ImportedSymbolResolver,
)
from codenerva.application.parsing.local_import_resolver import LocalImportResolver
from codenerva.application.parsing.parser_registry import ParserRegistry
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.application.parsing.symbol_extractor_registry import (
    SymbolExtractorRegistry,
)
from codenerva.application.parsing.symbol_mapper import (
    SymbolMapper,
)
from codenerva.application.parsing.typescript_path_alias_resolver import (
    TypeScriptPathAliasResolver,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.snapshot import Snapshot
from codenerva.domain.source_file import SourceFile
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


def test_analyze_python_source_file(
    tmp_path: Path,
) -> None:
    source_file_store = InMemorySourceFileStore()

    repository_id = uuid4()
    # snapshot_id = uuid4()
    snapshot_store = InMemorySnapshotStore()

    snapshot = Snapshot.create(
        repository_id=repository_id,
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/shop",
    )

    snapshot_store.save(snapshot)
    repository_path = tmp_path / "repositories" / str(repository_id)
    repository_path.mkdir(parents=True)

    file_path = repository_path / "service.py"

    file_path.write_text(
        """
from pathlib import Path

class AuthService:
    def login(self, email):
        return email
""",
        encoding="utf-8",
    )

    source_file = SourceFile.create(
        snapshot_id=snapshot.id,
        relative_path=PurePosixPath("service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=file_path.stat().st_size,
        content_hash="a" * 64,
    )

    source_file_store.save_many((source_file,))
    symbol_store = InMemorySymbolStore()
    symbol_relation_store = InMemorySymbolRelationStore()
    import_reference_store = InMemoryImportReferenceStore()
    source_file_relation_store = InMemorySourceFileRelationStore()

    use_case = AnalyzeSourceFileUseCase(
        source_file_store=source_file_store,
        snapshot_store=snapshot_store,
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
            typescript_path_alias_resolver=TypeScriptPathAliasResolver(),
        ),
        call_extractor_registry=CallExtractorRegistry(),
        build_call_relations_service=BuildCallRelationsService(
            imported_symbol_resolver=ImportedSymbolResolver(
                source_file_relation_store=source_file_relation_store,
                symbol_store=symbol_store,
            ),
        ),
    )

    result = use_case.execute(
        source_file_id=source_file.id,
    )
    relations = symbol_relation_store.list_by_source_symbol_id(result.symbols[0].id)

    assert len(relations) == 1
    assert relations[0].target_symbol_id == result.symbols[1].id
    assert result.has_parse_errors is False
    assert len(result.symbols) == 2

    references = import_reference_store.list_by_source_file_id(source_file.id)

    assert len(references) == 1
    assert references[0].module == "pathlib"
    assert references[0].imported_name == "Path"
    assert references[0].alias is None

    assert result.symbols[0].qualified_name == "AuthService"
    assert result.symbols[1].qualified_name == "AuthService.login"
    saved_symbols = symbol_store.list_by_source_file_id(source_file.id)

    assert len(saved_symbols) == 2
    assert saved_symbols[0].qualified_name == "AuthService"
    assert saved_symbols[1].qualified_name == "AuthService.login"
