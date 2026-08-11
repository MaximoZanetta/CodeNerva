from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True, slots=True)
class VectorRecord:
    chunk_id: UUID
    vector: tuple[float, ...]
    snapshot_id: UUID
    source_file_id: UUID
    symbol_id: UUID
    relative_path: str
    language: str
    qualified_name: str
    symbol_kind: str
