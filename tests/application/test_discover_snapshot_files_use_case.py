from pathlib import Path
from uuid import uuid4

import pytest

from codenerva.application.source.discover_snapshot_files import (
    DiscoverSnapshotFilesUseCase,
    SnapshotNotFoundError,
)
from codenerva.application.source.file_discovery import (
    FileDiscoveryService,
)
from codenerva.application.source.language_detector import (
    LanguageDetector,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.snapshot import Snapshot
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)


def test_discover_snapshot_files_use_case(
    tmp_path: Path,
) -> None:
    snapshot_store = InMemorySnapshotStore()
    source_file_store = InMemorySourceFileStore()

    repository_id = uuid4()
    snapshot = Snapshot.create(
        repository_id=repository_id,
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/shop",
    )
    snapshot_store.save(snapshot)

    repository_path = tmp_path / "repositories" / str(repository_id)
    repository_path.mkdir(parents=True)

    (repository_path / "main.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )
    (repository_path / "README.md").write_text(
        "# Example",
        encoding="utf-8",
    )
    (repository_path / "config.json").write_text(
        "{}",
        encoding="utf-8",
    )

    use_case = DiscoverSnapshotFilesUseCase(
        snapshot_store=snapshot_store,
        source_file_store=source_file_store,
        file_discovery_service=FileDiscoveryService(
            language_detector=LanguageDetector(),
        ),
        storage_root=tmp_path,
    )

    result = use_case.execute(snapshot.id)

    summaries = {summary.language: summary for summary in result.languages}

    saved_files = source_file_store.list_by_snapshot_id(snapshot.id)

    assert len(saved_files) == 3
    assert str(saved_files[0].relative_path) == "README.md"
    assert str(saved_files[1].relative_path) == "config.json"
    assert str(saved_files[2].relative_path) == "main.py"

    assert result.snapshot_id == snapshot.id
    assert result.total_files == 3
    assert summaries[ProgrammingLanguage.PYTHON].file_count == 1
    assert summaries[ProgrammingLanguage.MARKDOWN].file_count == 1
    assert summaries[ProgrammingLanguage.JSON].file_count == 1


def test_discover_snapshot_files_requires_snapshot(
    tmp_path: Path,
) -> None:
    use_case = DiscoverSnapshotFilesUseCase(
        snapshot_store=InMemorySnapshotStore(),
        source_file_store=InMemorySourceFileStore(),
        file_discovery_service=FileDiscoveryService(
            language_detector=LanguageDetector(),
        ),
        storage_root=tmp_path,
    )

    with pytest.raises(SnapshotNotFoundError):
        use_case.execute(uuid4())
