from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.infrastructure.database.base import Base
from codenerva.infrastructure.database.models.symbol_model import (
    SymbolModel,
)
from codenerva.infrastructure.database.postgres_symbol_store import (
    PostgresSymbolStore,
)


def test_postgres_symbol_store_round_trip() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
    )

    _ = SymbolModel

    Base.metadata.create_all(
        bind=engine,
    )

    session_factory = sessionmaker[Session](
        bind=engine,
        expire_on_commit=False,
    )

    store = PostgresSymbolStore(
        session_factory=session_factory,
    )

    source_file_id = uuid4()

    parent = Symbol.create(
        source_file_id=source_file_id,
        name="AuthService",
        qualified_name="AuthService",
        kind=SymbolKind.CLASS,
        start_line=1,
        end_line=20,
    )

    child = Symbol.create(
        source_file_id=source_file_id,
        name="login",
        qualified_name="AuthService.login",
        kind=SymbolKind.METHOD,
        start_line=5,
        end_line=10,
        parent_symbol_id=parent.id,
    )

    store.save_many(
        (
            parent,
            child,
        )
    )

    loaded_parent = store.get_by_id(parent.id)

    loaded_child = store.get_by_id(child.id)

    assert loaded_parent == parent
    assert loaded_child == child

    listed = store.list_by_source_file_id(source_file_id)

    assert listed == (
        parent,
        child,
    )
