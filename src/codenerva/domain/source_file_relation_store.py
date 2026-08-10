from typing import Protocol
from uuid import UUID

from codenerva.domain.source_file_relation import SourceFileRelation


class SourceFileRelationStore(Protocol):
    def save_many(
        self,
        relations: tuple[SourceFileRelation, ...],
    ) -> None: ...

    def list_by_source_file_id(
        self,
        source_file_id: UUID,
    ) -> tuple[SourceFileRelation, ...]: ...

    def list_by_target_file_id(
        self,
        target_file_id: UUID,
    ) -> tuple[SourceFileRelation, ...]: ...
