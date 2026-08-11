from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from codenerva.application.chunking.symbol_chunker import SymbolChunker
from codenerva.application.embeddings.embed_chunks import EmbedChunksUseCase
from codenerva.domain.chunk_store import ChunkStore
from codenerva.domain.snapshot_store import SnapshotStore
from codenerva.domain.source_file_store import SourceFileStore
from codenerva.domain.symbol_store import SymbolStore


class SnapshotNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class IndexSnapshotResult:
    snapshot_id: UUID
    total_files: int
    indexed_files: int
    skipped_files: int
    indexed_chunks: int


class IndexSnapshotUseCase:
    def __init__(
        self,
        *,
        snapshot_store: SnapshotStore,
        source_file_store: SourceFileStore,
        symbol_store: SymbolStore,
        chunk_store: ChunkStore,
        symbol_chunker: SymbolChunker,
        embed_chunks_use_case: EmbedChunksUseCase,
        storage_root: Path,
    ) -> None:
        self._snapshot_store = snapshot_store
        self._source_file_store = source_file_store
        self._symbol_store = symbol_store
        self._chunk_store = chunk_store
        self._symbol_chunker = symbol_chunker
        self._embed_chunks_use_case = embed_chunks_use_case
        self._storage_root = storage_root

    def execute(
        self,
        *,
        snapshot_id: UUID,
    ) -> IndexSnapshotResult:
        snapshot = self._snapshot_store.get_by_id(snapshot_id)

        if snapshot is None:
            raise SnapshotNotFoundError(
                f"Snapshot with id {snapshot_id} was not found."
            )

        source_files = self._source_file_store.list_by_snapshot_id(snapshot_id)

        repository_path = (
            self._storage_root / "repositories" / str(snapshot.repository_id)
        )

        indexed_files = 0
        skipped_files = 0
        indexed_chunks = 0

        for source_file in source_files:
            symbols = self._symbol_store.list_by_source_file_id(source_file.id)

            if not symbols:
                skipped_files += 1
                continue

            file_path = repository_path / Path(source_file.relative_path.as_posix())

            if not file_path.exists():
                skipped_files += 1
                continue

            try:
                source = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                skipped_files += 1
                continue

            chunks = self._symbol_chunker.chunk(
                source_file=source_file,
                symbols=symbols,
                source=source,
            )

            if not chunks:
                skipped_files += 1
                continue

            self._chunk_store.save_many(chunks)

            embed_result = self._embed_chunks_use_case.execute(
                chunks=chunks,
            )

            indexed_files += 1
            indexed_chunks += embed_result.embedded_chunks

        return IndexSnapshotResult(
            snapshot_id=snapshot.id,
            total_files=len(source_files),
            indexed_files=indexed_files,
            skipped_files=skipped_files,
            indexed_chunks=indexed_chunks,
        )
