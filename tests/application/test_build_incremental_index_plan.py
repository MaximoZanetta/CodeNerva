from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.snapshots.build_incremental_index_plan import (
    BuildIncrementalIndexPlanUseCase,
)
from codenerva.application.snapshots.compare_snapshots import (
    CompareSnapshotsResult,
    FileChange,
    FileChangeKind,
)


def test_build_incremental_index_plan() -> None:
    previous_snapshot_id = uuid4()
    current_snapshot_id = uuid4()

    previous_unchanged_id = uuid4()
    current_unchanged_id = uuid4()

    previous_modified_id = uuid4()
    current_modified_id = uuid4()

    added_id = uuid4()
    deleted_id = uuid4()

    comparison = CompareSnapshotsResult(
        previous_snapshot_id=previous_snapshot_id,
        current_snapshot_id=current_snapshot_id,
        changes=(
            FileChange(
                relative_path=PurePosixPath("unchanged.py"),
                kind=FileChangeKind.UNCHANGED,
                previous_source_file_id=(previous_unchanged_id),
                current_source_file_id=(current_unchanged_id),
            ),
            FileChange(
                relative_path=PurePosixPath("modified.py"),
                kind=FileChangeKind.MODIFIED,
                previous_source_file_id=(previous_modified_id),
                current_source_file_id=(current_modified_id),
            ),
            FileChange(
                relative_path=PurePosixPath("added.py"),
                kind=FileChangeKind.ADDED,
                previous_source_file_id=None,
                current_source_file_id=added_id,
            ),
            FileChange(
                relative_path=PurePosixPath("deleted.py"),
                kind=FileChangeKind.DELETED,
                previous_source_file_id=deleted_id,
                current_source_file_id=None,
            ),
        ),
    )

    result = BuildIncrementalIndexPlanUseCase().execute(comparison=comparison)

    assert result.previous_snapshot_id == (previous_snapshot_id)

    assert result.current_snapshot_id == (current_snapshot_id)

    assert result.reuse_source_file_ids == (current_unchanged_id,)

    assert result.analyze_source_file_ids == (
        current_modified_id,
        added_id,
    )

    assert result.deleted_source_file_ids == (deleted_id,)

    assert result.reused_files == 1
    assert result.analyzed_files == 2
    assert result.deleted_files == 1
