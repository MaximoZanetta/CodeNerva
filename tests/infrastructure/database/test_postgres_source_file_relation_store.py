from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.source_file_relation import (
    SourceFileRelation,
    SourceFileRelationKind,
)
from codenerva.infrastructure.database.base import Base
from codenerva.infrastructure.database.models.source_file_relation_model import (
    SourceFileRelationModel,
)
from codenerva.infrastructure.database.postgres_source_file_relation_store import (
    PostgresSourceFileRelationStore,
)


def test_postgres_source_file_relation_store_round_trip() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
    )

    _ = SourceFileRelationModel

    Base.metadata.create_all(
        bind=engine,
    )

    session_factory = sessionmaker[Session](
        bind=engine,
        expire_on_commit=False,
    )

    store = PostgresSourceFileRelationStore(
        session_factory=session_factory,
    )

    source_file_id = uuid4()
    target_file_id = uuid4()

    relation = SourceFileRelation.create(
        source_file_id=source_file_id,
        target_file_id=target_file_id,
        kind=SourceFileRelationKind.IMPORTS,
    )

    store.save_many((relation,))

    by_source = store.list_by_source_file_id(source_file_id)

    by_target = store.list_by_target_file_id(target_file_id)

    assert by_source == (relation,)

    assert by_target == (relation,)
