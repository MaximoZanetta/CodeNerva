from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid5

SOURCE_FILE_RELATION_NAMESPACE = UUID("6c43cd72-86c2-4fdb-8f50-6438c4f9f73d")


class SourceFileRelationKind(StrEnum):
    IMPORTS = "IMPORTS"


@dataclass(frozen=True, slots=True)
class SourceFileRelation:
    id: UUID
    source_file_id: UUID
    target_file_id: UUID
    kind: SourceFileRelationKind

    @classmethod
    def create(
        cls,
        *,
        source_file_id: UUID,
        target_file_id: UUID,
        kind: SourceFileRelationKind,
    ) -> "SourceFileRelation":
        if source_file_id == target_file_id:
            raise ValueError("A source file cannot relate to itself.")

        relation_id = uuid5(
            SOURCE_FILE_RELATION_NAMESPACE,
            (f"{source_file_id}:{kind.value}:{target_file_id}"),
        )

        return cls(
            id=relation_id,
            source_file_id=source_file_id,
            target_file_id=target_file_id,
            kind=kind,
        )
