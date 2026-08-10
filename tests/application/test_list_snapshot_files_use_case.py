from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from codenerva.application.source.list_snapshot_files import (
    ListSnapshotFilesUseCase,
    SnapshotNotFoundError,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.snapshot import Snapshot
from codenerva.domain.source_file import SourceFile
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)


def test_list_snapshot_files() -> None:
    snapshot_store = InMemorySnapshotStore()
    source_file_store = InMemorySourceFileStore()

    snapshot = Snapshot.create(
        repository_id=uuid4(),
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/shop",
    )
    snapshot_store.save(snapshot)

    source_file_store.save_many(
        (
            SourceFile.create(
                snapshot_id=snapshot.id,
                relative_path=PurePosixPath("src/main.py"),
                language=ProgrammingLanguage.PYTHON,
                size_bytes=120,
                content_hash="b" * 64,
            ),
            SourceFile.create(
                snapshot_id=snapshot.id,
                relative_path=PurePosixPath("README.md"),
                language=ProgrammingLanguage.MARKDOWN,
                size_bytes=80,
                content_hash="b" * 64,
            ),
        )
    )

    use_case = ListSnapshotFilesUseCase(
        snapshot_store=snapshot_store,
        source_file_store=source_file_store,
    )

    result = use_case.execute(snapshot.id)

    assert result.snapshot_id == snapshot.id
    assert len(result.files) == 2
    assert result.files[0].relative_path == "README.md"
    assert result.files[1].relative_path == "src/main.py"


def test_list_snapshot_files_requires_snapshot() -> None:
    use_case = ListSnapshotFilesUseCase(
        snapshot_store=InMemorySnapshotStore(),
        source_file_store=InMemorySourceFileStore(),
    )

    with pytest.raises(SnapshotNotFoundError):
        use_case.execute(uuid4())
