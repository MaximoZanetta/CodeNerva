import math
from uuid import UUID

from codenerva.domain.vector_record import VectorRecord
from codenerva.domain.vector_search_result import VectorSearchResult
from codenerva.domain.vector_store import VectorStore


class InMemoryVectorStore(VectorStore):
    def __init__(self) -> None:
        self._records: dict[UUID, VectorRecord] = {}

    def save_many(
        self,
        records: tuple[VectorRecord, ...],
    ) -> None:
        for record in records:
            self._records[record.chunk_id] = record

    def get_by_chunk_id(
        self,
        chunk_id: UUID,
    ) -> VectorRecord | None:
        return self._records.get(chunk_id)

    def search(
        self,
        *,
        query_vector: tuple[float, ...],
        top_k: int,
        snapshot_id: UUID,
    ) -> tuple[VectorSearchResult, ...]:
        if top_k <= 0:
            raise ValueError("top_k must be positive.")

        if not query_vector:
            raise ValueError("query_vector cannot be empty.")

        candidates = tuple(
            record
            for record in self._records.values()
            if record.snapshot_id == snapshot_id
        )

        scored = [
            VectorSearchResult(
                record=record,
                score=self._cosine_similarity(
                    query_vector,
                    record.vector,
                ),
            )
            for record in candidates
        ]

        scored.sort(
            key=lambda result: result.score,
            reverse=True,
        )

        return tuple(scored[:top_k])

    def _cosine_similarity(
        self,
        first: tuple[float, ...],
        second: tuple[float, ...],
    ) -> float:
        dot_product = sum(
            first_value * second_value
            for first_value, second_value in zip(
                first,
                second,
                strict=True,
            )
        )

        first_norm = math.sqrt(sum(value * value for value in first))

        second_norm = math.sqrt(sum(value * value for value in second))

        if first_norm == 0 or second_norm == 0:
            return 0.0

        return dot_product / (first_norm * second_norm)
