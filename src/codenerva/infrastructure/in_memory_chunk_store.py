from uuid import UUID

from codenerva.domain.chunk import Chunk
from codenerva.domain.chunk_store import ChunkStore


class InMemoryChunkStore(ChunkStore):
    def __init__(self) -> None:
        self._chunks: dict[UUID, Chunk] = {}

    def save_many(
        self,
        chunks: tuple[Chunk, ...],
    ) -> None:
        for chunk in chunks:
            self._chunks[chunk.id] = chunk

    def get_by_id(
        self,
        chunk_id: UUID,
    ) -> Chunk | None:
        return self._chunks.get(chunk_id)

    def list_by_symbol_id(
        self,
        symbol_id: UUID,
    ) -> tuple[Chunk, ...]:
        return tuple(
            chunk for chunk in self._chunks.values() if chunk.symbol_id == symbol_id
        )

    def delete_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> int:
        chunk_ids = [
            chunk_id
            for chunk_id, chunk in self._chunks.items()
            if chunk.snapshot_id == snapshot_id
        ]

        for chunk_id in chunk_ids:
            del self._chunks[chunk_id]

        return len(chunk_ids)
