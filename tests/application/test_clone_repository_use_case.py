from pathlib import Path
from uuid import uuid4

import pytest

from codenerva.application.repository.clone_repository import (
    CloneRepositoryUseCase,
    RepositoryNotFoundError,
)
from codenerva.domain.repository import Repository
from codenerva.infrastructure.in_memory_repository_store import (
    InMemoryRepositoryStore,
)


class FakeGitClient:
    def __init__(self) -> None:
        self.remote_url: str | None = None
        self.destination: Path | None = None

    def clone(
        self,
        *,
        remote_url: str,
        destination: Path,
    ) -> None:
        self.remote_url = remote_url
        self.destination = destination


def test_clone_repository_use_case(tmp_path: Path) -> None:
    repository_store = InMemoryRepositoryStore()
    git_client = FakeGitClient()

    repository = Repository.create_github(
        project_id=uuid4(),
        remote_url="https://github.com/example/shop",
    )
    repository_store.save(repository)

    use_case = CloneRepositoryUseCase(
        repository_store=repository_store,
        git_client=git_client,
        storage_root=tmp_path,
    )

    result = use_case.execute(repository.id)

    expected_destination = tmp_path / "repositories" / str(repository.id)

    assert result.repository_id == repository.id
    assert result.destination == expected_destination
    assert git_client.remote_url == repository.remote_url
    assert git_client.destination == expected_destination


def test_clone_repository_requires_existing_repository(
    tmp_path: Path,
) -> None:
    use_case = CloneRepositoryUseCase(
        repository_store=InMemoryRepositoryStore(),
        git_client=FakeGitClient(),
        storage_root=tmp_path,
    )

    with pytest.raises(RepositoryNotFoundError):
        use_case.execute(uuid4())
