from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.snapshot_store import SnapshotStore
from codenerva.domain.source_file_store import SourceFileStore


class SnapshotNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class SourceFileResult:
    id: UUID
    relative_path: str
    language: ProgrammingLanguage
    size_bytes: int
    content_hash: str


@dataclass(frozen=True, slots=True)
class ListSnapshotFilesResult:
    snapshot_id: UUID
    files: tuple[SourceFileResult, ...]


class ListSnapshotFilesUseCase:
    def __init__(
        self,
        *,
        snapshot_store: SnapshotStore,
        source_file_store: SourceFileStore,
    ) -> None:
        self._snapshot_store = snapshot_store
        self._source_file_store = source_file_store

    def execute(
        self,
        snapshot_id: UUID,
    ) -> ListSnapshotFilesResult:
        snapshot = self._snapshot_store.get_by_id(snapshot_id)

        if snapshot is None:
            raise SnapshotNotFoundError(
                f"Snapshot with id {snapshot_id} was not found."
            )

        source_files = self._source_file_store.list_by_snapshot_id(snapshot_id)

        return ListSnapshotFilesResult(
            snapshot_id=snapshot_id,
            files=tuple(
                SourceFileResult(
                    id=source_file.id,
                    relative_path=str(source_file.relative_path),
                    language=source_file.language,
                    size_bytes=source_file.size_bytes,
                    content_hash=source_file.content_hash,
                )
                for source_file in source_files
            ),
        )
