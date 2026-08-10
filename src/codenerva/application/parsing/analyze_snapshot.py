from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from tree_sitter import Tree

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
    CallExtractorNotAvailableError,
    CallExtractorRegistry,
)
from codenerva.application.parsing.import_extractor_registry import (
    ImportExtractorNotAvailableError,
    ImportExtractorRegistry,
)
from codenerva.application.parsing.import_reference_mapper import ImportReferenceMapper
from codenerva.application.parsing.parser_registry import ParserNotAvailableError
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.application.parsing.symbol_extractor_registry import (
    SymbolExtractorNotAvailableError,
    SymbolExtractorRegistry,
)
from codenerva.application.parsing.symbol_mapper import (
    SymbolMapper,
)
from codenerva.domain.import_reference import ImportReference
from codenerva.domain.import_reference_store import ImportReferenceStore
from codenerva.domain.snapshot_store import SnapshotStore
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation_store import SourceFileRelationStore
from codenerva.domain.source_file_store import SourceFileStore
from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_relation_store import SymbolRelationStore
from codenerva.domain.symbol_store import SymbolStore


class SnapshotNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class AnalyzeSnapshotResult:
    snapshot_id: UUID
    total_files: int
    analyzed_files: int
    skipped_files: int
    files_with_parse_errors: int
    total_symbols: int


@dataclass(frozen=True, slots=True)
class _AnalyzedFile:
    source_file: SourceFile
    tree: Tree
    source: bytes
    symbols: tuple[Symbol, ...]
    import_references: tuple[ImportReference, ...]


class AnalyzeSnapshotUseCase:
    def __init__(
        self,
        *,
        snapshot_store: SnapshotStore,
        source_file_store: SourceFileStore,
        symbol_store: SymbolStore,
        source_parser: SourceParser,
        symbol_extractor_registry: SymbolExtractorRegistry,
        symbol_mapper: SymbolMapper,
        storage_root: Path,
        symbol_relation_store: SymbolRelationStore,
        build_symbol_relations_service: BuildSymbolRelationsService,
        import_reference_store: ImportReferenceStore,
        import_extractor_registry: ImportExtractorRegistry,
        import_reference_mapper: ImportReferenceMapper,
        source_file_relation_store: SourceFileRelationStore,
        build_source_file_relations_service: BuildSourceFileRelationsService,
        call_extractor_registry: CallExtractorRegistry,
        build_call_relations_service: BuildCallRelationsService,
    ) -> None:
        self._snapshot_store = snapshot_store
        self._source_file_store = source_file_store
        self._symbol_store = symbol_store
        self._source_parser = source_parser
        self._symbol_extractor_registry = symbol_extractor_registry
        self._symbol_mapper = symbol_mapper
        self._storage_root = storage_root
        self._symbol_relation_store = symbol_relation_store
        self._build_symbol_relations_service = build_symbol_relations_service
        self._import_reference_store = import_reference_store
        self._import_extractor_registry = import_extractor_registry
        self._import_reference_mapper = import_reference_mapper
        self._source_file_relation_store = source_file_relation_store
        self._build_source_file_relations_service = build_source_file_relations_service
        self._call_extractor_registry = call_extractor_registry
        self._build_call_relations_service = build_call_relations_service

    def execute(
        self,
        snapshot_id: UUID,
    ) -> AnalyzeSnapshotResult:
        snapshot = self._snapshot_store.get_by_id(snapshot_id)

        if snapshot is None:
            raise SnapshotNotFoundError(
                f"Snapshot with id {snapshot_id} was not found."
            )

        source_files = self._source_file_store.list_by_snapshot_id(snapshot_id)

        analyzed_files = 0
        skipped_files = 0
        files_with_parse_errors = 0
        total_symbols = 0

        analyzed_source_files: list[_AnalyzedFile] = []

        repository_path = (
            self._storage_root / "repositories" / str(snapshot.repository_id)
        )

        # PASS 1:
        # Parsear todos los archivos y persistir symbols/imports.
        for source_file in source_files:
            file_path = repository_path / Path(source_file.relative_path.as_posix())

            try:
                extractor = self._symbol_extractor_registry.get(source_file.language)
            except SymbolExtractorNotAvailableError:
                skipped_files += 1
                continue

            try:
                source = file_path.read_bytes()

                parse_result = self._source_parser.parse(
                    language=source_file.language,
                    source=source,
                )
            except ParserNotAvailableError:
                skipped_files += 1
                continue

            # Symbols
            extracted_symbols = extractor.extract(
                tree=parse_result.tree,
                source=source,
            )

            symbols = self._symbol_mapper.map(
                source_file_id=source_file.id,
                extracted_symbols=extracted_symbols,
            )

            self._symbol_store.save_many(symbols)

            # CONTAINS
            symbol_relations = self._build_symbol_relations_service.build(
                symbols=symbols,
            )

            self._symbol_relation_store.save_many(symbol_relations)

            # Imports
            import_references: tuple[ImportReference, ...] = ()

            try:
                import_extractor = self._import_extractor_registry.get(
                    source_file.language
                )
            except ImportExtractorNotAvailableError:
                import_extractor = None

            if import_extractor is not None:
                extracted_imports = import_extractor.extract(
                    tree=parse_result.tree,
                    source=source,
                )

                import_references = self._import_reference_mapper.map(
                    source_file_id=source_file.id,
                    extracted_imports=extracted_imports,
                )

                self._import_reference_store.save_many(import_references)

                source_file_relations = self._build_source_file_relations_service.build(
                    source_file=source_file,
                    import_references=import_references,
                    snapshot_files=source_files,
                )

                self._source_file_relation_store.save_many(source_file_relations)

            analyzed_source_files.append(
                _AnalyzedFile(
                    source_file=source_file,
                    tree=parse_result.tree,
                    source=source,
                    symbols=symbols,
                    import_references=import_references,
                )
            )

            analyzed_files += 1
            total_symbols += len(symbols)

            if parse_result.has_errors:
                files_with_parse_errors += 1

        # PASS 2:
        # Ahora todos los symbols del snapshot ya existen.
        # Recién acá resolvemos CALLS.
        for analyzed_file in analyzed_source_files:
            try:
                call_extractor = self._call_extractor_registry.get(
                    analyzed_file.source_file.language
                )
            except CallExtractorNotAvailableError:
                continue

            extracted_calls = call_extractor.extract(
                tree=analyzed_file.tree,
                source=analyzed_file.source,
            )

            call_relations = self._build_call_relations_service.build(
                calls=extracted_calls,
                symbols=analyzed_file.symbols,
                import_references=(analyzed_file.import_references),
            )

            self._symbol_relation_store.save_many(call_relations)

        return AnalyzeSnapshotResult(
            snapshot_id=snapshot.id,
            total_files=len(source_files),
            analyzed_files=analyzed_files,
            skipped_files=skipped_files,
            files_with_parse_errors=files_with_parse_errors,
            total_symbols=total_symbols,
        )
