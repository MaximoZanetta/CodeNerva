from pathlib import Path
from uuid import uuid4

from codenerva.application.repository.clone_repository import (
    CloneRepositoryUseCase,
)
from codenerva.domain.repository import Repository
from codenerva.infrastructure.in_memory_repository_store import (
    InMemoryRepositoryStore,
)
from codenerva.infrastructure.subprocess_git_client import (
    SubprocessGitClient,
)


def main() -> None:
    repository_store = InMemoryRepositoryStore()

    repository = Repository.create_github(
        project_id=uuid4(),
        remote_url="https://github.com/octocat/Hello-World",
    )
    repository_store.save(repository)

    use_case = CloneRepositoryUseCase(
        repository_store=repository_store,
        git_client=SubprocessGitClient(),
        storage_root=Path("storage"),
    )

    result = use_case.execute(repository.id)

    print(f"Repository cloned into: {result.destination}")


if __name__ == "__main__":
    main()
