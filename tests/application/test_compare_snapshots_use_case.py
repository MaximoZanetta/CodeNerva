from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.snapshots.compare_snapshots import (
    CompareSnapshotsUseCase,
    FileChangeKind,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)


def test_compare_snapshots_detects_all_change_kinds() -> None:
    previous_snapshot_id = uuid4()
    current_snapshot_id = uuid4()

    store = InMemorySourceFileStore()

    previous_unchanged = SourceFile.create(
        snapshot_id=previous_snapshot_id,
        relative_path=PurePosixPath("unchanged.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=10,
        content_hash="a" * 64,
    )

    current_unchanged = SourceFile.create(
        snapshot_id=current_snapshot_id,
        relative_path=PurePosixPath("unchanged.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=10,
        content_hash="a" * 64,
    )

    previous_modified = SourceFile.create(
        snapshot_id=previous_snapshot_id,
        relative_path=PurePosixPath("modified.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=10,
        content_hash="b" * 64,
    )

    current_modified = SourceFile.create(
        snapshot_id=current_snapshot_id,
        relative_path=PurePosixPath("modified.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=20,
        content_hash="c" * 64,
    )

    deleted = SourceFile.create(
        snapshot_id=previous_snapshot_id,
        relative_path=PurePosixPath("deleted.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=10,
        content_hash="d" * 64,
    )

    added = SourceFile.create(
        snapshot_id=current_snapshot_id,
        relative_path=PurePosixPath("added.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=10,
        content_hash="e" * 64,
    )

    store.save_many(
        (
            previous_unchanged,
            previous_modified,
            deleted,
            current_unchanged,
            current_modified,
            added,
        )
    )

    result = CompareSnapshotsUseCase(
        source_file_store=store,
    ).execute(
        previous_snapshot_id=previous_snapshot_id,
        current_snapshot_id=current_snapshot_id,
    )

    changes = {
        change.relative_path.as_posix(): change.kind for change in result.changes
    }

    assert changes == {
        "added.py": FileChangeKind.ADDED,
        "deleted.py": FileChangeKind.DELETED,
        "modified.py": FileChangeKind.MODIFIED,
        "unchanged.py": FileChangeKind.UNCHANGED,
    }

    assert result.added_files == 1
    assert result.deleted_files == 1
    assert result.modified_files == 1
    assert result.unchanged_files == 1
