from uuid import uuid4

import pytest

from codenerva.application.project.get_project import (
    GetProjectUseCase,
    ProjectNotFoundError,
)
from codenerva.domain.project import Project
from codenerva.infrastructure.in_memory_project_repository import (
    InMemoryProjectRepository,
)


def test_get_project_use_case() -> None:
    repository = InMemoryProjectRepository()
    project = Project.create(name="CodeNerva")
    repository.save(project)

    use_case = GetProjectUseCase(repository)

    result = use_case.execute(project.id)

    assert result.id == project.id
    assert result.name == "CodeNerva"
    assert result.status == "ACTIVE"


def test_get_project_raises_when_not_found() -> None:
    repository = InMemoryProjectRepository()
    use_case = GetProjectUseCase(repository)

    with pytest.raises(ProjectNotFoundError):
        use_case.execute(uuid4())
