from typing import Protocol
from uuid import UUID

from codenerva.domain.chunk import Chunk


class ChunkStore(Protocol):
    def save_many(
        self,
        chunks: tuple[Chunk, ...],
    ) -> None: ...

    def get_by_id(
        self,
        chunk_id: UUID,
    ) -> Chunk | None: ...

    def list_by_symbol_id(
        self,
        symbol_id: UUID,
    ) -> tuple[Chunk, ...]: ...

    def delete_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> int: ...
