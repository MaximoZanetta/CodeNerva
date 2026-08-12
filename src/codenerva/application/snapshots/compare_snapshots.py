from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath
from uuid import UUID

from codenerva.domain.source_file_store import SourceFileStore


class FileChangeKind(StrEnum):
    UNCHANGED = "UNCHANGED"
    MODIFIED = "MODIFIED"
    ADDED = "ADDED"
    DELETED = "DELETED"


@dataclass(frozen=True, slots=True)
class FileChange:
    relative_path: PurePosixPath
    kind: FileChangeKind
    previous_source_file_id: UUID | None
    current_source_file_id: UUID | None


@dataclass(frozen=True, slots=True)
class CompareSnapshotsResult:
    previous_snapshot_id: UUID
    current_snapshot_id: UUID
    changes: tuple[FileChange, ...]

    @property
    def unchanged_files(self) -> int:
        return sum(
            1 for change in self.changes if change.kind == FileChangeKind.UNCHANGED
        )

    @property
    def modified_files(self) -> int:
        return sum(
            1 for change in self.changes if change.kind == FileChangeKind.MODIFIED
        )

    @property
    def added_files(self) -> int:
        return sum(1 for change in self.changes if change.kind == FileChangeKind.ADDED)

    @property
    def deleted_files(self) -> int:
        return sum(
            1 for change in self.changes if change.kind == FileChangeKind.DELETED
        )


class CompareSnapshotsUseCase:
    def __init__(
        self,
        *,
        source_file_store: SourceFileStore,
    ) -> None:
        self._source_file_store = source_file_store

    def execute(
        self,
        *,
        previous_snapshot_id: UUID,
        current_snapshot_id: UUID,
    ) -> CompareSnapshotsResult:
        if previous_snapshot_id == current_snapshot_id:
            raise ValueError("Snapshots to compare must be different.")

        previous_files = self._source_file_store.list_by_snapshot_id(
            previous_snapshot_id
        )

        current_files = self._source_file_store.list_by_snapshot_id(current_snapshot_id)

        previous_by_path = {file.relative_path: file for file in previous_files}

        current_by_path = {file.relative_path: file for file in current_files}

        all_paths = sorted(
            set(previous_by_path) | set(current_by_path),
            key=lambda path: path.as_posix(),
        )

        changes: list[FileChange] = []

        for path in all_paths:
            previous = previous_by_path.get(path)
            current = current_by_path.get(path)

            if previous is None:
                changes.append(
                    FileChange(
                        relative_path=path,
                        kind=FileChangeKind.ADDED,
                        previous_source_file_id=None,
                        current_source_file_id=current.id,
                    )
                )
                continue

            if current is None:
                changes.append(
                    FileChange(
                        relative_path=path,
                        kind=FileChangeKind.DELETED,
                        previous_source_file_id=previous.id,
                        current_source_file_id=None,
                    )
                )
                continue

            if previous.content_hash == current.content_hash:
                kind = FileChangeKind.UNCHANGED
            else:
                kind = FileChangeKind.MODIFIED

            changes.append(
                FileChange(
                    relative_path=path,
                    kind=kind,
                    previous_source_file_id=previous.id,
                    current_source_file_id=current.id,
                )
            )

        return CompareSnapshotsResult(
            previous_snapshot_id=previous_snapshot_id,
            current_snapshot_id=current_snapshot_id,
            changes=tuple(changes),
        )
