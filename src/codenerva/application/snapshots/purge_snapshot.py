from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.chunk_store import ChunkStore
from codenerva.domain.import_reference_store import (
    ImportReferenceStore,
)
from codenerva.domain.snapshot_store import SnapshotStore
from codenerva.domain.source_file_relation_store import (
    SourceFileRelationStore,
)
from codenerva.domain.source_file_store import SourceFileStore
from codenerva.domain.symbol_relation_store import (
    SymbolRelationStore,
)
from codenerva.domain.symbol_store import SymbolStore
from codenerva.domain.vector_store import VectorStore


class SnapshotNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class PurgeSnapshotResult:
    snapshot_id: UUID

    deleted_vectors: int
    deleted_symbol_relations: int
    deleted_source_file_relations: int
    deleted_import_references: int
    deleted_chunks: int
    deleted_symbols: int
    deleted_source_files: int

    snapshot_deleted: bool


class PurgeSnapshotUseCase:
    def __init__(
        self,
        *,
        snapshot_store: SnapshotStore,
        source_file_store: SourceFileStore,
        symbol_store: SymbolStore,
        symbol_relation_store: SymbolRelationStore,
        source_file_relation_store: SourceFileRelationStore,
        import_reference_store: ImportReferenceStore,
        chunk_store: ChunkStore,
        vector_store: VectorStore,
    ) -> None:
        self._snapshot_store = snapshot_store
        self._source_file_store = source_file_store
        self._symbol_store = symbol_store
        self._symbol_relation_store = symbol_relation_store
        self._source_file_relation_store = source_file_relation_store
        self._import_reference_store = import_reference_store
        self._chunk_store = chunk_store
        self._vector_store = vector_store

    def execute(
        self,
        *,
        snapshot_id: UUID,
    ) -> PurgeSnapshotResult:
        snapshot = self._snapshot_store.get_by_id(snapshot_id)

        if snapshot is None:
            raise SnapshotNotFoundError(
                f"Snapshot with id {snapshot_id} was not found."
            )

        source_files = self._source_file_store.list_by_snapshot_id(snapshot_id)

        source_file_ids = tuple(source_file.id for source_file in source_files)

        symbol_ids: list[UUID] = []

        for source_file_id in source_file_ids:
            symbols = self._symbol_store.list_by_source_file_id(source_file_id)

            symbol_ids.extend(symbol.id for symbol in symbols)

        symbol_ids_tuple = tuple(symbol_ids)

        # Qdrant first.
        deleted_vectors = self._vector_store.delete_by_snapshot_id(snapshot_id)

        # Delete relationships before their nodes.
        deleted_symbol_relations = self._symbol_relation_store.delete_by_symbol_ids(
            symbol_ids_tuple
        )

        deleted_source_file_relations = (
            self._source_file_relation_store.delete_by_source_file_ids(source_file_ids)
        )

        deleted_import_references = (
            self._import_reference_store.delete_by_source_file_ids(source_file_ids)
        )

        deleted_chunks = self._chunk_store.delete_by_snapshot_id(snapshot_id)

        deleted_symbols = self._symbol_store.delete_by_source_file_ids(source_file_ids)

        deleted_source_files = self._source_file_store.delete_by_snapshot_id(
            snapshot_id
        )

        snapshot_deleted = self._snapshot_store.delete(snapshot_id)

        return PurgeSnapshotResult(
            snapshot_id=snapshot_id,
            deleted_vectors=deleted_vectors,
            deleted_symbol_relations=(deleted_symbol_relations),
            deleted_source_file_relations=(deleted_source_file_relations),
            deleted_import_references=(deleted_import_references),
            deleted_chunks=deleted_chunks,
            deleted_symbols=deleted_symbols,
            deleted_source_files=(deleted_source_files),
            snapshot_deleted=snapshot_deleted,
        )
