from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.project_repository import ProjectRepository
from codenerva.domain.repository import Repository
from codenerva.domain.repository_store import RepositoryStore


class ProjectNotFoundError(Exception):
    pass


class RepositoryAlreadyExistsError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class RegisterRepositoryCommand:
    project_id: UUID
    remote_url: str


@dataclass(frozen=True, slots=True)
class RegisterRepositoryResult:
    id: UUID
    project_id: UUID
    remote_url: str
    owner: str
    name: str
    status: str


class RegisterRepositoryUseCase:
    def __init__(
        self,
        project_repository: ProjectRepository,
        repository_store: RepositoryStore,
    ) -> None:
        self._project_repository = project_repository
        self._repository_store = repository_store

    def execute(
        self,
        command: RegisterRepositoryCommand,
    ) -> RegisterRepositoryResult:
        project = self._project_repository.get_by_id(command.project_id)

        if project is None:
            raise ProjectNotFoundError(
                f"Project with id {command.project_id} was not found."
            )

        existing_repository = self._repository_store.get_by_project_id(
            command.project_id
        )

        if existing_repository is not None:
            raise RepositoryAlreadyExistsError("This project already has a repository.")

        repository = Repository.create_github(
            project_id=command.project_id,
            remote_url=command.remote_url,
        )

        self._repository_store.save(repository)

        return RegisterRepositoryResult(
            id=repository.id,
            project_id=repository.project_id,
            remote_url=repository.remote_url,
            owner=repository.owner,
            name=repository.name,
            status=repository.status.value,
        )
