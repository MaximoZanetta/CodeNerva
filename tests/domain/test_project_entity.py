import pytest

from codenerva.domain.project import Project, ProjectStatus


def test_create_project() -> None:
    project = Project.create(
        name="CodeNerva",
        description="Code intelligence platform",
    )

    assert project.name == "CodeNerva"
    assert project.description == "Code intelligence platform"
    assert project.status is ProjectStatus.ACTIVE


def test_project_name_is_trimmed() -> None:
    project = Project.create(name="  CodeNerva  ")

    assert project.name == "CodeNerva"


def test_empty_project_name_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="Project name cannot be empty",
    ):
        Project.create(name="   ")


def test_blank_description_becomes_none() -> None:
    project = Project.create(
        name="CodeNerva",
        description="   ",
    )

    assert project.description is None
