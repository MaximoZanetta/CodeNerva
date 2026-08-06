from uuid import uuid4

import pytest

from codenerva.application.repository.register_repository import (
    ProjectNotFoundError,
    RegisterRepositoryCommand,
    RegisterRepositoryUseCase,
    RepositoryAlreadyExistsError,
)
from codenerva.domain.project import Project
from codenerva.infrastructure.in_memory_project_repository import (
    InMemoryProjectRepository,
)
from codenerva.infrastructure.in_memory_repository_store import (
    InMemoryRepositoryStore,
)


def test_register_repository() -> None:
    project_repository = InMemoryProjectRepository()
    repository_store = InMemoryRepositoryStore()

    project = Project.create(name="CodeNerva")
    project_repository.save(project)

    use_case = RegisterRepositoryUseCase(
        project_repository,
        repository_store,
    )

    result = use_case.execute(
        RegisterRepositoryCommand(
            project_id=project.id,
            remote_url="https://github.com/example/shop",
        )
    )

    saved_repository = repository_store.get_by_id(result.id)

    assert saved_repository is not None
    assert result.project_id == project.id
    assert result.owner == "example"
    assert result.name == "shop"
    assert result.status == "ACTIVE"


def test_register_repository_requires_existing_project() -> None:
    use_case = RegisterRepositoryUseCase(
        InMemoryProjectRepository(),
        InMemoryRepositoryStore(),
    )

    with pytest.raises(ProjectNotFoundError):
        use_case.execute(
            RegisterRepositoryCommand(
                project_id=uuid4(),
                remote_url="https://github.com/example/shop",
            )
        )


def test_project_cannot_have_two_repositories() -> None:
    project_repository = InMemoryProjectRepository()
    repository_store = InMemoryRepositoryStore()

    project = Project.create(name="CodeNerva")
    project_repository.save(project)

    use_case = RegisterRepositoryUseCase(
        project_repository,
        repository_store,
    )

    command = RegisterRepositoryCommand(
        project_id=project.id,
        remote_url="https://github.com/example/shop",
    )

    use_case.execute(command)

    with pytest.raises(RepositoryAlreadyExistsError):
        use_case.execute(command)
