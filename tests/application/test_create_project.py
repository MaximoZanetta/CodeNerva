from codenerva.application.project.create_project import (
    CreateProjectCommand,
    CreateProjectUseCase,
)
from codenerva.infrastructure.in_memory_project_repository import (
    InMemoryProjectRepository,
)


def test_create_project_use_case() -> None:
    repository = InMemoryProjectRepository()
    use_case = CreateProjectUseCase(repository)

    result = use_case.execute(
        CreateProjectCommand(
            name="CodeNerva",
            description="Code intelligence platform",
        )
    )

    saved_project = repository.get_by_id(result.id)

    assert saved_project is not None
    assert result.name == "CodeNerva"
    assert result.description == "Code intelligence platform"
    assert result.status == "ACTIVE"
    assert saved_project.id == result.id


import pytest


def test_create_project_rejects_empty_name() -> None:
    repository = InMemoryProjectRepository()
    use_case = CreateProjectUseCase(repository)

    with pytest.raises(
        ValueError,
        match="Project name cannot be empty",
    ):
        use_case.execute(CreateProjectCommand(name="   "))
