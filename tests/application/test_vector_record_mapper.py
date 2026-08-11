from uuid import uuid4

from codenerva.application.embeddings.vector_record_mapper import (
    VectorRecordMapper,
)
from codenerva.domain.chunk import Chunk


def test_map_chunks_to_vector_records() -> None:
    chunk = Chunk.create(
        snapshot_id=uuid4(),
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        text="def login(): pass",
        relative_path="auth.py",
        language="python",
        qualified_name="login",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=1,
        code="def login(): pass",
    )

    mapper = VectorRecordMapper()

    records = mapper.map(
        chunks=(chunk,),
        vectors=((0.1, 0.2, 0.3),),
    )

    assert len(records) == 1

    record = records[0]

    assert record.chunk_id == chunk.id
    assert record.symbol_id == chunk.symbol_id
    assert record.vector == (0.1, 0.2, 0.3)
