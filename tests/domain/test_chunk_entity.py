from uuid import uuid4

import pytest

from codenerva.domain.chunk import Chunk


def test_create_chunk() -> None:
    chunk = Chunk.create(
        snapshot_id=uuid4(),
        source_file_id=uuid4(),
        symbol_id=uuid4(),
        text="def login():\n    pass",
        relative_path="services/auth.py",
        language="python",
        qualified_name="AuthService.login",
        symbol_kind="METHOD",
        start_line=10,
        end_line=11,
        code="def login(): pass",
    )

    assert chunk.text
    assert chunk.qualified_name == "AuthService.login"
    assert chunk.part_index == 0
    assert chunk.part_count == 1


def test_chunk_id_is_deterministic() -> None:
    snapshot_id = uuid4()
    source_file_id = uuid4()
    symbol_id = uuid4()

    first = Chunk.create(
        snapshot_id=snapshot_id,
        source_file_id=source_file_id,
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

    second = Chunk.create(
        snapshot_id=snapshot_id,
        source_file_id=source_file_id,
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

    assert first.id == second.id


def test_chunk_rejects_empty_text() -> None:
    with pytest.raises(ValueError):
        Chunk.create(
            snapshot_id=uuid4(),
            source_file_id=uuid4(),
            symbol_id=uuid4(),
            text="   ",
            relative_path="auth.py",
            language="python",
            qualified_name="login",
            symbol_kind="FUNCTION",
            start_line=1,
            end_line=1,
            code="def login(): pass",
        )
