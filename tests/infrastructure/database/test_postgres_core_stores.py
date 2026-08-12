from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.project import Project
from codenerva.domain.repository import Repository
from codenerva.domain.snapshot import Snapshot
from codenerva.infrastructure.database.base import Base
from codenerva.infrastructure.database.models.project_model import (
    ProjectModel,
)
from codenerva.infrastructure.database.models.repository_model import (
    RepositoryModel,
)
from codenerva.infrastructure.database.models.snapshot_model import (
    SnapshotModel,
)
from codenerva.infrastructure.database.postgres_project_repository import (
    PostgresProjectRepository,
)
from codenerva.infrastructure.database.postgres_repository_store import (
    PostgresRepositoryStore,
)
from codenerva.infrastructure.database.postgres_snapshot_store import (
    PostgresSnapshotStore,
)


def test_persist_project_repository_and_snapshot() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
    )

    _ = (
        ProjectModel,
        RepositoryModel,
        SnapshotModel,
    )

    Base.metadata.create_all(
        bind=engine,
    )

    session_factory = sessionmaker[Session](
        bind=engine,
        expire_on_commit=False,
    )

    project_repository = PostgresProjectRepository(
        session_factory=session_factory,
    )

    repository_store = PostgresRepositoryStore(
        session_factory=session_factory,
    )

    snapshot_store = PostgresSnapshotStore(
        session_factory=session_factory,
    )

    project = Project.create(
        name="CodeNerva Test",
        description="Persistence test",
    )

    project_repository.save(project)

    repository = Repository.create_github(
        project_id=project.id,
        remote_url=("https://github.com/example/repo"),
    )

    repository_store.save(repository)

    snapshot = Snapshot.create(
        repository_id=repository.id,
        commit_sha="a" * 40,
        branch="main",
        remote_url=repository.remote_url,
    )

    snapshot_store.save(snapshot)

    loaded_project = project_repository.get_by_id(project.id)

    loaded_repository = repository_store.get_by_id(repository.id)

    loaded_snapshot = snapshot_store.get_by_id(snapshot.id)

    assert loaded_project == project
    assert loaded_repository == repository
    assert loaded_snapshot == snapshot
