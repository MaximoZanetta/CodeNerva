from pathlib import Path
from uuid import uuid4

import pytest

from codenerva.application.git.git_client import GitRepositoryInfo
from codenerva.application.repository.create_snapshot import (
    CreateSnapshotUseCase,
    RepositoryNotFoundError,
    SnapshotAlreadyExistsError,
)
from codenerva.domain.repository import Repository
from codenerva.infrastructure.in_memory_repository_store import (
    InMemoryRepositoryStore,
)
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)


class FakeGitClient:
    def __init__(self, info: GitRepositoryInfo) -> None:
        self.info = info
        self.inspected_path: Path | None = None

    def clone(
        self,
        *,
        remote_url: str,
        destination: Path,
    ) -> None:
        raise NotImplementedError

    def inspect(
        self,
        *,
        repository_path: Path,
    ) -> GitRepositoryInfo:
        self.inspected_path = repository_path
        return self.info


def test_create_snapshot_use_case(tmp_path: Path) -> None:
    repository_store = InMemoryRepositoryStore()
    snapshot_store = InMemorySnapshotStore()

    repository = Repository.create_github(
        project_id=uuid4(),
        remote_url="https://github.com/example/shop",
    )
    repository_store.save(repository)

    git_client = FakeGitClient(
        GitRepositoryInfo(
            commit_sha="a" * 40,
            branch="main",
            remote_url="https://github.com/example/shop",
        )
    )

    use_case = CreateSnapshotUseCase(
        repository_store=repository_store,
        snapshot_store=snapshot_store,
        git_client=git_client,
        storage_root=tmp_path,
    )

    result = use_case.execute(repository.id)

    saved_snapshot = snapshot_store.get_by_id(result.id)
    expected_path = tmp_path / "repositories" / str(repository.id)

    assert saved_snapshot is not None
    assert result.repository_id == repository.id
    assert result.commit_sha == "a" * 40
    assert result.branch == "main"
    assert result.status == "PENDING"
    assert git_client.inspected_path == expected_path


def test_create_snapshot_requires_existing_repository(
    tmp_path: Path,
) -> None:
    use_case = CreateSnapshotUseCase(
        repository_store=InMemoryRepositoryStore(),
        snapshot_store=InMemorySnapshotStore(),
        git_client=FakeGitClient(
            GitRepositoryInfo(
                commit_sha="a" * 40,
                branch="main",
                remote_url="https://github.com/example/shop",
            )
        ),
        storage_root=tmp_path,
    )

    with pytest.raises(RepositoryNotFoundError):
        use_case.execute(uuid4())


def test_snapshot_cannot_be_duplicated(
    tmp_path: Path,
) -> None:
    repository_store = InMemoryRepositoryStore()
    snapshot_store = InMemorySnapshotStore()

    repository = Repository.create_github(
        project_id=uuid4(),
        remote_url="https://github.com/example/shop",
    )
    repository_store.save(repository)

    git_client = FakeGitClient(
        GitRepositoryInfo(
            commit_sha="a" * 40,
            branch="main",
            remote_url="https://github.com/example/shop",
        )
    )

    use_case = CreateSnapshotUseCase(
        repository_store=repository_store,
        snapshot_store=snapshot_store,
        git_client=git_client,
        storage_root=tmp_path,
    )

    use_case.execute(repository.id)

    with pytest.raises(SnapshotAlreadyExistsError):
        use_case.execute(repository.id)
