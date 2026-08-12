from dataclasses import dataclass
from uuid import UUID

from codenerva.application.snapshots.compare_snapshots import (
    CompareSnapshotsResult,
    FileChangeKind,
)


@dataclass(frozen=True, slots=True)
class IncrementalIndexPlan:
    previous_snapshot_id: UUID
    current_snapshot_id: UUID

    reuse_source_file_ids: tuple[UUID, ...]
    analyze_source_file_ids: tuple[UUID, ...]
    deleted_source_file_ids: tuple[UUID, ...]

    @property
    def reused_files(self) -> int:
        return len(self.reuse_source_file_ids)

    @property
    def analyzed_files(self) -> int:
        return len(self.analyze_source_file_ids)

    @property
    def deleted_files(self) -> int:
        return len(self.deleted_source_file_ids)


class BuildIncrementalIndexPlanUseCase:
    def execute(
        self,
        *,
        comparison: CompareSnapshotsResult,
    ) -> IncrementalIndexPlan:
        reuse_source_file_ids: list[UUID] = []
        analyze_source_file_ids: list[UUID] = []
        deleted_source_file_ids: list[UUID] = []

        for change in comparison.changes:
            if change.kind == FileChangeKind.UNCHANGED:
                if change.current_source_file_id is None:
                    raise ValueError("UNCHANGED file must have a current source file.")

                reuse_source_file_ids.append(change.current_source_file_id)

                continue

            if change.kind in {
                FileChangeKind.MODIFIED,
                FileChangeKind.ADDED,
            }:
                if change.current_source_file_id is None:
                    raise ValueError("File to analyze must have a current source file.")

                analyze_source_file_ids.append(change.current_source_file_id)

                continue

            if change.kind == FileChangeKind.DELETED:
                if change.previous_source_file_id is None:
                    raise ValueError("DELETED file must have a previous source file.")

                deleted_source_file_ids.append(change.previous_source_file_id)

        return IncrementalIndexPlan(
            previous_snapshot_id=(comparison.previous_snapshot_id),
            current_snapshot_id=(comparison.current_snapshot_id),
            reuse_source_file_ids=tuple(reuse_source_file_ids),
            analyze_source_file_ids=tuple(analyze_source_file_ids),
            deleted_source_file_ids=tuple(deleted_source_file_ids),
        )
