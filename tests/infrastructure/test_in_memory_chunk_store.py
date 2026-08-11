from uuid import uuid4

from codenerva.domain.chunk import Chunk
from codenerva.infrastructure.in_memory_chunk_store import (
    InMemoryChunkStore,
)


def test_save_and_find_chunks_by_symbol() -> None:
    symbol_id = uuid4()

    chunk = Chunk.create(
        snapshot_id=uuid4(),
        source_file_id=uuid4(),
        symbol_id=symbol_id,
        text="def login(): pass",
        relative_path="auth.py",
        language="python",
        qualified_name="login",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=1,
        code="def login(): pass",
    )

    store = InMemoryChunkStore()

    store.save_many((chunk,))

    result = store.list_by_symbol_id(symbol_id)

    assert len(result) == 1
    assert result[0] == chunk
