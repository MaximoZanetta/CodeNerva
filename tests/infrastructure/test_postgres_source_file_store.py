from pathlib import PurePosixPath
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.infrastructure.database.base import Base
from codenerva.infrastructure.database.models.source_file_model import (
    SourceFileModel,
)
from codenerva.infrastructure.database.postgres_source_file_store import (
    PostgresSourceFileStore,
)


def test_postgres_source_file_store_round_trip() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
    )

    _ = SourceFileModel

    Base.metadata.create_all(
        bind=engine,
    )

    session_factory = sessionmaker[Session](
        bind=engine,
        expire_on_commit=False,
    )

    store = PostgresSourceFileStore(
        session_factory=session_factory,
    )

    snapshot_id = uuid4()

    source_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/example.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=42,
        content_hash="a" * 64,
    )

    store.save_many((source_file,))

    loaded = store.get_by_id(source_file.id)

    assert loaded == source_file

    listed = store.list_by_snapshot_id(snapshot_id)

    assert listed == (source_file,)
