from dataclasses import dataclass

from codenerva.domain.vector_record import VectorRecord


@dataclass(frozen=True, slots=True)
class VectorSearchResult:
    record: VectorRecord
    score: float
