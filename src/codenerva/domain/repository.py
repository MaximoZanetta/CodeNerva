from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID, uuid4


class RepositoryProvider(StrEnum):
    GITHUB = "GITHUB"


class RepositoryStatus(StrEnum):
    ACTIVE = "ACTIVE"
    UNAVAILABLE = "UNAVAILABLE"


@dataclass(frozen=True, slots=True)
class Repository:
    id: UUID
    project_id: UUID
    provider: RepositoryProvider
    remote_url: str
    owner: str
    name: str
    status: RepositoryStatus

    @classmethod
    def create_github(
        cls,
        *,
        project_id: UUID,
        remote_url: str,
    ) -> "Repository":
        normalized_url = remote_url.strip().removesuffix("/").removesuffix(".git")

        prefix = "https://github.com/"
        if not normalized_url.startswith(prefix):
            raise ValueError("Repository URL must be a valid GitHub HTTPS URL.")

        path = normalized_url.removeprefix(prefix)
        parts = path.split("/")

        if len(parts) != 2 or not all(parts):
            raise ValueError(
                "Repository URL must contain an owner and repository name."
            )

        owner, name = parts

        return cls(
            id=uuid4(),
            project_id=project_id,
            provider=RepositoryProvider.GITHUB,
            remote_url=normalized_url,
            owner=owner,
            name=name,
            status=RepositoryStatus.ACTIVE,
        )
