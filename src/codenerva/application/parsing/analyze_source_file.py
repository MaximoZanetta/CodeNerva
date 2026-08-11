from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

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
from codenerva.application.parsing.parser_registry import (
    ParserNotAvailableError,
)
from codenerva.application.parsing.source_parser import SourceParser
from codenerva.application.parsing.symbol_extractor_registry import (
    SymbolExtractorNotAvailableError,
    SymbolExtractorRegistry,
)
from codenerva.application.parsing.symbol_mapper import (
    SymbolMapper,
)
from codenerva.domain.import_reference_store import ImportReferenceStore
from codenerva.domain.snapshot_store import SnapshotStore
from codenerva.domain.source_file_relation_store import SourceFileRelationStore
from codenerva.domain.source_file_store import SourceFileStore
from codenerva.domain.symbol import Symbol
from codenerva.domain.symbol_relation_store import SymbolRelationStore
from codenerva.domain.symbol_store import SymbolStore


class SourceFileNotFoundError(Exception):
    pass


class SymbolAnalysisNotAvailableError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class AnalyzeSourceFileResult:
    source_file_id: UUID
    symbols: tuple[Symbol, ...]
    has_parse_errors: bool


class AnalyzeSourceFileUseCase:
    def __init__(
        self,
        *,
        source_file_store: SourceFileStore,
        snapshot_store: SnapshotStore,
        symbol_store: SymbolStore,
        symbol_relation_store: SymbolRelationStore,
        source_parser: SourceParser,
        symbol_extractor_registry: SymbolExtractorRegistry,
        symbol_mapper: SymbolMapper,
        build_symbol_relations_service: BuildSymbolRelationsService,
        storage_root: Path,
        import_reference_store: ImportReferenceStore,
        import_extractor_registry: ImportExtractorRegistry,
        import_reference_mapper: ImportReferenceMapper,
        source_file_relation_store: SourceFileRelationStore,
        build_source_file_relations_service: BuildSourceFileRelationsService,
        call_extractor_registry: CallExtractorRegistry,
        build_call_relations_service: BuildCallRelationsService,
    ) -> None:
        self._source_file_store = source_file_store
        self._snapshot_store = snapshot_store
        self._symbol_store = symbol_store
        self._symbol_relation_store = symbol_relation_store
        self._source_parser = source_parser
        self._symbol_extractor_registry = symbol_extractor_registry
        self._symbol_mapper = symbol_mapper
        self._build_symbol_relations_service = build_symbol_relations_service
        self._storage_root = storage_root
        self._import_reference_store = import_reference_store
        self._import_extractor_registry = import_extractor_registry
        self._import_reference_mapper = import_reference_mapper
        self._source_file_relation_store = source_file_relation_store
        self._build_source_file_relations_service = build_source_file_relations_service
        self._call_extractor_registry = call_extractor_registry
        self._build_call_relations_service = build_call_relations_service

    def execute(
        self,
        *,
        source_file_id: UUID,
    ) -> AnalyzeSourceFileResult:
        source_file = self._source_file_store.get_by_id(source_file_id)

        if source_file is None:
            raise SourceFileNotFoundError(
                f"Source file with id {source_file_id} was not found."
            )

        snapshot = self._snapshot_store.get_by_id(source_file.snapshot_id)

        if snapshot is None:
            raise RuntimeError("Snapshot referenced by SourceFile does not exist.")

        file_path = (
            self._storage_root
            / "repositories"
            / str(snapshot.repository_id)
            / Path(source_file.relative_path.as_posix())
        )

        try:
            extractor = self._symbol_extractor_registry.get(source_file.language)
        except SymbolExtractorNotAvailableError as exc:
            raise SymbolAnalysisNotAvailableError(
                f"Symbol analysis is not available for {source_file.language.value}."
            ) from exc

        try:
            source = file_path.read_bytes()

            parse_result = self._source_parser.parse(
                language=source_file.language,
                source=source,
            )
        except ParserNotAvailableError as exc:
            raise SymbolAnalysisNotAvailableError(
                f"Parser is not available for {source_file.language.value}."
            ) from exc

        # 1. Symbols
        extracted_symbols = extractor.extract(
            tree=parse_result.tree,
            source=source,
        )

        symbols = self._symbol_mapper.map(
            source_file_id=source_file.id,
            extracted_symbols=extracted_symbols,
        )

        self._symbol_store.save_many(symbols)

        # 2. CONTAINS relations
        symbol_relations = self._build_symbol_relations_service.build(
            symbols=symbols,
        )

        self._symbol_relation_store.save_many(symbol_relations)

        # 3. Imports
        import_references = ()

        try:
            import_extractor = self._import_extractor_registry.get(source_file.language)
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

            snapshot_files = self._source_file_store.list_by_snapshot_id(
                source_file.snapshot_id
            )

            source_file_relations = self._build_source_file_relations_service.build(
                source_file=source_file,
                import_references=import_references,
                snapshot_files=snapshot_files,
                repository_path=(
                    self._storage_root / "repositories" / str(snapshot.repository_id)
                ),
            )

            self._source_file_relation_store.save_many(source_file_relations)

        # 4. Calls
        try:
            call_extractor = self._call_extractor_registry.get(source_file.language)
        except CallExtractorNotAvailableError:
            call_extractor = None

        if call_extractor is not None:
            extracted_calls = call_extractor.extract(
                tree=parse_result.tree,
                source=source,
            )

            call_relations = self._build_call_relations_service.build(
                calls=extracted_calls,
                symbols=symbols,
                import_references=import_references,
            )

            self._symbol_relation_store.save_many(call_relations)

        return AnalyzeSourceFileResult(
            source_file_id=source_file.id,
            symbols=symbols,
            has_parse_errors=parse_result.has_errors,
        )
