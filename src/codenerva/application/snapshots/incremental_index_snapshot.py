from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from codenerva.application.chunking.symbol_chunker import SymbolChunker
from codenerva.application.embeddings.embed_chunks import EmbedChunksUseCase
from codenerva.application.parsing.analyze_source_file import (
    AnalyzeSourceFileUseCase,
    SymbolAnalysisNotAvailableError,
)
from codenerva.application.snapshots.build_incremental_index_plan import (
    BuildIncrementalIndexPlanUseCase,
)
from codenerva.application.snapshots.compare_snapshots import (
    CompareSnapshotsUseCase,
)
from codenerva.application.snapshots.reuse_cross_file_relations import (
    ReuseCrossFileRelationsUseCase,
)
from codenerva.application.snapshots.reuse_unchanged_file import (
    ReuseUnchangedFileUseCase,
)
from codenerva.domain.chunk_store import ChunkStore
from codenerva.domain.snapshot_store import SnapshotStore
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_store import SourceFileStore


@dataclass(frozen=True, slots=True)
class IncrementalIndexSnapshotResult:
    previous_snapshot_id: UUID
    current_snapshot_id: UUID

    reused_files: int
    analyzed_files: int
    skipped_files: int
    deleted_files: int

    reused_symbols: int
    reused_symbol_relations: int
    reused_source_file_relations: int
    reused_chunks: int
    reused_vectors: int

    indexed_chunks: int


class IncrementalIndexSnapshotUseCase:
    def __init__(
        self,
        *,
        source_file_store: SourceFileStore,
        compare_snapshots_use_case: CompareSnapshotsUseCase,
        build_plan_use_case: BuildIncrementalIndexPlanUseCase,
        reuse_unchanged_file_use_case: ReuseUnchangedFileUseCase,
        reuse_cross_file_relations_use_case: ReuseCrossFileRelationsUseCase,
        analyze_source_file_use_case: AnalyzeSourceFileUseCase,
        snapshot_store: SnapshotStore,
        symbol_chunker: SymbolChunker,
        chunk_store: ChunkStore,
        embed_chunks_use_case: EmbedChunksUseCase,
        storage_root: Path,
    ) -> None:
        self._source_file_store = source_file_store
        self._compare_snapshots_use_case = compare_snapshots_use_case
        self._build_plan_use_case = build_plan_use_case
        self._reuse_unchanged_file_use_case = reuse_unchanged_file_use_case
        self._reuse_cross_file_relations_use_case = reuse_cross_file_relations_use_case
        self._analyze_source_file_use_case = analyze_source_file_use_case
        self._snapshot_store = snapshot_store
        self._symbol_chunker = symbol_chunker
        self._chunk_store = chunk_store
        self._embed_chunks_use_case = embed_chunks_use_case
        self._storage_root = storage_root

    def execute(
        self,
        *,
        previous_snapshot_id: UUID,
        current_snapshot_id: UUID,
    ) -> IncrementalIndexSnapshotResult:
        comparison = self._compare_snapshots_use_case.execute(
            previous_snapshot_id=previous_snapshot_id,
            current_snapshot_id=current_snapshot_id,
        )

        plan = self._build_plan_use_case.execute(comparison=comparison)

        previous_files = self._source_file_store.list_by_snapshot_id(
            previous_snapshot_id
        )

        previous_by_path = {
            source_file.relative_path: source_file for source_file in previous_files
        }

        reused_file_pairs: list[tuple[SourceFile, SourceFile]] = []

        reused_symbols = 0
        reused_symbol_relations = 0
        reused_chunks = 0
        reused_vectors = 0

        # 1. Reuse unchanged files.
        for current_source_file_id in plan.reuse_source_file_ids:
            current_source_file = self._source_file_store.get_by_id(
                current_source_file_id
            )

            if current_source_file is None:
                raise ValueError("Current source file to reuse was not found.")

            previous_source_file = previous_by_path.get(
                current_source_file.relative_path
            )

            if previous_source_file is None:
                raise ValueError("Previous source file to reuse was not found.")

            reuse_result = self._reuse_unchanged_file_use_case.execute(
                previous_source_file=previous_source_file,
                current_source_file=current_source_file,
            )

            reused_file_pairs.append(
                (
                    previous_source_file,
                    current_source_file,
                )
            )

            reused_symbols += reuse_result.reused_symbols

            reused_symbol_relations += reuse_result.reused_symbol_relations

            reused_chunks += reuse_result.reused_chunks

            reused_vectors += reuse_result.reused_vectors

        # 2. Rebuild cross-file relationships
        # between unchanged files.
        cross_file_result = self._reuse_cross_file_relations_use_case.execute(
            file_pairs=tuple(reused_file_pairs)
        )

        reused_symbol_relations += cross_file_result.reused_symbol_relations

        # 3. Resolve current snapshot.
        current_snapshot = self._snapshot_store.get_by_id(current_snapshot_id)

        if current_snapshot is None:
            raise ValueError("Current snapshot was not found.")

        repository_path = (
            self._storage_root / "repositories" / str(current_snapshot.repository_id)
        )

        analyzed_files = 0
        skipped_files = 0
        indexed_chunks = 0

        # 4. Analyze and index only ADDED / MODIFIED files.
        for source_file_id in plan.analyze_source_file_ids:
            source_file = self._source_file_store.get_by_id(source_file_id)

            if source_file is None:
                raise ValueError("Source file to analyze was not found.")

            try:
                analysis_result = self._analyze_source_file_use_case.execute(
                    source_file_id=source_file.id,
                )
            except SymbolAnalysisNotAvailableError:
                skipped_files += 1
                continue

            file_path = repository_path / Path(source_file.relative_path.as_posix())

            try:
                source = file_path.read_text(encoding="utf-8")
            except (
                UnicodeDecodeError,
                OSError,
            ):
                skipped_files += 1
                continue

            chunks = self._symbol_chunker.chunk(
                source_file=source_file,
                symbols=analysis_result.symbols,
                source=source,
            )

            analyzed_files += 1

            if not chunks:
                continue

            self._chunk_store.save_many(chunks)

            embed_result = self._embed_chunks_use_case.execute(
                chunks=chunks,
            )

            indexed_chunks += embed_result.embedded_chunks

        return IncrementalIndexSnapshotResult(
            previous_snapshot_id=previous_snapshot_id,
            current_snapshot_id=current_snapshot_id,
            reused_files=plan.reused_files,
            analyzed_files=analyzed_files,
            skipped_files=skipped_files,
            deleted_files=plan.deleted_files,
            reused_symbols=reused_symbols,
            reused_symbol_relations=(reused_symbol_relations),
            reused_source_file_relations=(
                cross_file_result.reused_source_file_relations
            ),
            reused_chunks=reused_chunks,
            reused_vectors=reused_vectors,
            indexed_chunks=indexed_chunks,
        )
