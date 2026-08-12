from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.chunk import Chunk
from codenerva.infrastructure.database.base import Base
from codenerva.infrastructure.database.models.chunk_model import (
    ChunkModel,
)
from codenerva.infrastructure.database.postgres_chunk_store import (
    PostgresChunkStore,
)


def test_postgres_chunk_store_round_trip() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
    )

    _ = ChunkModel

    Base.metadata.create_all(
        bind=engine,
    )

    session_factory = sessionmaker[Session](
        bind=engine,
        expire_on_commit=False,
    )

    store = PostgresChunkStore(
        session_factory=session_factory,
    )

    snapshot_id = uuid4()
    source_file_id = uuid4()
    symbol_id = uuid4()

    chunk = Chunk.create(
        snapshot_id=snapshot_id,
        source_file_id=source_file_id,
        symbol_id=symbol_id,
        text=(
            "Language: python\n"
            "File: app.py\n"
            "Symbol: chat\n"
            "Kind: FUNCTION\n\n"
            "Code:\n"
            "def chat():\n"
            "    return True"
        ),
        relative_path="app.py",
        language="python",
        qualified_name="chat",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=2,
        code=("def chat():\n    return True"),
    )

    store.save_many((chunk,))

    loaded = store.get_by_id(chunk.id)

    assert loaded == chunk

    listed = store.list_by_symbol_id(symbol_id)

    assert listed == (chunk,)
