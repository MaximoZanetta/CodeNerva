from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4


class ProjectStatus(StrEnum):
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True, slots=True)
class Project:
    id: UUID
    name: str
    description: str | None
    status: ProjectStatus

    @classmethod
    def create(
        cls,
        *,
        name: str,
        description: str | None = None,
    ) -> "Project":
        normalized_name = name.strip()

        if not normalized_name:
            raise ValueError("Project name cannot be empty.")

        normalized_description = (
            description.strip() if description and description.strip() else None
        )

        return cls(
            id=uuid4(),
            name=normalized_name,
            description=normalized_description,
            status=ProjectStatus.ACTIVE,
        )
