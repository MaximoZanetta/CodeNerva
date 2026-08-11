from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid5

CHUNK_NAMESPACE = UUID("9fa4b5f7-3f9b-4ad0-a34e-a11e697ef790")


class ChunkKind(StrEnum):
    SYMBOL = "SYMBOL"


@dataclass(frozen=True, slots=True)
class Chunk:
    id: UUID
    snapshot_id: UUID
    source_file_id: UUID
    symbol_id: UUID
    kind: ChunkKind

    text: str

    relative_path: str
    language: str
    qualified_name: str
    symbol_kind: str

    start_line: int
    end_line: int

    part_index: int
    part_count: int
    code: str

    @classmethod
    def create(
        cls,
        *,
        snapshot_id: UUID,
        source_file_id: UUID,
        symbol_id: UUID,
        text: str,
        relative_path: str,
        language: str,
        qualified_name: str,
        symbol_kind: str,
        start_line: int,
        end_line: int,
        part_index: int = 0,
        part_count: int = 1,
        code: str,
    ) -> "Chunk":
        if not text.strip():
            raise ValueError("Chunk text cannot be empty.")

        if part_index < 0:
            raise ValueError("part_index cannot be negative.")

        if part_count <= 0:
            raise ValueError("part_count must be positive.")

        if part_index >= part_count:
            raise ValueError("part_index must be smaller than part_count.")
        if not code.strip():
            raise ValueError("Chunk code cannot be empty.")

        chunk_id = uuid5(
            CHUNK_NAMESPACE,
            (f"{snapshot_id}:{source_file_id}:{symbol_id}:{part_index}"),
        )

        return cls(
            id=chunk_id,
            snapshot_id=snapshot_id,
            source_file_id=source_file_id,
            symbol_id=symbol_id,
            kind=ChunkKind.SYMBOL,
            text=text,
            relative_path=relative_path,
            language=language,
            qualified_name=qualified_name,
            symbol_kind=symbol_kind,
            start_line=start_line,
            end_line=end_line,
            part_index=part_index,
            part_count=part_count,
            code=code,
        )
