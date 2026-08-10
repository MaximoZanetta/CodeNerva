from typing import Protocol
from uuid import UUID

from codenerva.domain.source_file import SourceFile


class SourceFileStore(Protocol):
    def save_many(
        self,
        source_files: tuple[SourceFile, ...],
    ) -> None: ...

    def list_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> tuple[SourceFile, ...]: ...

    def get_by_id(
        self,
        source_file_id: UUID,
    ) -> SourceFile | None: ...
