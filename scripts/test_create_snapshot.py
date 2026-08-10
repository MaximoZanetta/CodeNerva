from pathlib import Path
from uuid import UUID, uuid4

from codenerva.application.repository.create_snapshot import (
    CreateSnapshotUseCase,
)
from codenerva.domain.repository import (
    Repository,
    RepositoryProvider,
    RepositoryStatus,
)
from codenerva.infrastructure.in_memory_repository_store import (
    InMemoryRepositoryStore,
)
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)
from codenerva.infrastructure.subprocess_git_client import (
    SubprocessGitClient,
)


def main() -> None:
    repository_id = UUID("210d9d57-c492-4741-a999-e2fbf17c9b5d")

    repository_store = InMemoryRepositoryStore()
    snapshot_store = InMemorySnapshotStore()

    repository = Repository(
        id=repository_id,
        project_id=uuid4(),
        provider=RepositoryProvider.GITHUB,
        remote_url="https://github.com/octocat/Hello-World",
        owner="octocat",
        name="Hello-World",
        status=RepositoryStatus.ACTIVE,
    )

    repository_store.save(repository)

    use_case = CreateSnapshotUseCase(
        repository_store=repository_store,
        snapshot_store=snapshot_store,
        git_client=SubprocessGitClient(),
        storage_root=Path("storage"),
    )

    result = use_case.execute(repository.id)

    print(f"Snapshot ID: {result.id}")
    print(f"Repository ID: {result.repository_id}")
    print(f"Commit SHA: {result.commit_sha}")
    print(f"Branch: {result.branch}")
    print(f"Remote URL: {result.remote_url}")
    print(f"Status: {result.status}")


if __name__ == "__main__":
    main()
