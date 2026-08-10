from pathlib import Path, PurePosixPath
from uuid import uuid4

from codenerva.application.parsing.analyze_snapshot import (
    AnalyzeSnapshotUseCase,
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

# from codenerva.application.parsing.python_symbol_extractor import (
#     PythonSymbolExtractor,
# )
from codenerva.application.parsing.symbol_mapper import (
    SymbolMapper,
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


def test_analyze_snapshot(
    tmp_path: Path,
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
        remote_url="https://github.com/example/shop",
    )
    snapshot_store.save(snapshot)

    repository_path = tmp_path / "repositories" / str(repository_id)
    repository_path.mkdir(parents=True)

    python_path = repository_path / "service.py"
    python_path.write_text(
        """
class AuthService:
    def login(self):
        pass
""",
        encoding="utf-8",
    )

    markdown_path = repository_path / "README.md"
    markdown_path.write_text(
        "# Example",
        encoding="utf-8",
    )

    source_file_store.save_many(
        (
            SourceFile.create(
                snapshot_id=snapshot.id,
                relative_path=PurePosixPath("service.py"),
                language=ProgrammingLanguage.PYTHON,
                size_bytes=python_path.stat().st_size,
                content_hash="a" * 64,
            ),
            SourceFile.create(
                snapshot_id=snapshot.id,
                relative_path=PurePosixPath("README.md"),
                language=ProgrammingLanguage.MARKDOWN,
                size_bytes=markdown_path.stat().st_size,
                content_hash="b" * 64,
            ),
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
            ),
        ),
    )

    result = use_case.execute(snapshot.id)

    assert result.total_files == 2
    assert result.analyzed_files == 1
    assert result.skipped_files == 1
    assert result.files_with_parse_errors == 0
    assert result.total_symbols == 2
