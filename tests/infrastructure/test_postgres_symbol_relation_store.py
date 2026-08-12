from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.symbol_relation import (
    SymbolRelation,
    SymbolRelationKind,
)
from codenerva.infrastructure.database.base import Base
from codenerva.infrastructure.database.models.symbol_relation_model import (
    SymbolRelationModel,
)
from codenerva.infrastructure.database.postgres_symbol_relation_store import (
    PostgresSymbolRelationStore,
)


def test_postgres_symbol_relation_store_round_trip() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
    )

    _ = SymbolRelationModel

    Base.metadata.create_all(
        bind=engine,
    )

    session_factory = sessionmaker[Session](
        bind=engine,
        expire_on_commit=False,
    )

    store = PostgresSymbolRelationStore(
        session_factory=session_factory,
    )

    source_symbol_id = uuid4()
    target_symbol_id = uuid4()

    relation = SymbolRelation.create(
        source_symbol_id=source_symbol_id,
        target_symbol_id=target_symbol_id,
        kind=SymbolRelationKind.CALLS,
    )

    store.save_many((relation,))

    by_source = store.list_by_source_symbol_id(source_symbol_id)

    by_target = store.list_by_target_symbol_id(target_symbol_id)

    assert by_source == (relation,)

    assert by_target == (relation,)
