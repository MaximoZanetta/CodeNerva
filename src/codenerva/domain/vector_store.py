from typing import Protocol
from uuid import UUID

from codenerva.domain.vector_record import VectorRecord
from codenerva.domain.vector_search_result import VectorSearchResult


class VectorStore(Protocol):
    def save_many(
        self,
        records: tuple[VectorRecord, ...],
    ) -> None: ...

    def get_by_chunk_id(
        self,
        chunk_id: UUID,
    ) -> VectorRecord | None: ...

    def search(
        self,
        *,
        query_vector: tuple[float, ...],
        top_k: int,
        snapshot_id: UUID,
    ) -> tuple[VectorSearchResult, ...]: ...

    def delete_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> int: ...
