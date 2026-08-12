from uuid import UUID

from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_store import SourceFileStore


class InMemorySourceFileStore(SourceFileStore):
    def __init__(self) -> None:
        self._source_files: dict[UUID, SourceFile] = {}

    def save_many(
        self,
        source_files: tuple[SourceFile, ...],
    ) -> None:
        for source_file in source_files:
            self._source_files[source_file.id] = source_file

    def list_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> tuple[SourceFile, ...]:
        matching_files = (
            source_file
            for source_file in self._source_files.values()
            if source_file.snapshot_id == snapshot_id
        )

        return tuple(
            sorted(
                matching_files,
                key=lambda source_file: str(source_file.relative_path),
            )
        )

    def get_by_id(
        self,
        source_file_id: UUID,
    ) -> SourceFile | None:
        return self._source_files.get(source_file_id)

    def delete_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> int:
        source_file_ids = [
            source_file_id
            for source_file_id, source_file in self._source_files.items()
            if source_file.snapshot_id == snapshot_id
        ]

        for source_file_id in source_file_ids:
            del self._source_files[source_file_id]

        return len(source_file_ids)
