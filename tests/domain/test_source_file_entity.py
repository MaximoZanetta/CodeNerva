from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile


def test_source_file_id_is_deterministic() -> None:
    snapshot_id = uuid4()

    first = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/main.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    second = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/main.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    assert first.id == second.id


def test_same_path_in_different_snapshots_has_different_id() -> None:
    first = SourceFile.create(
        snapshot_id=uuid4(),
        relative_path=PurePosixPath("src/main.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    second = SourceFile.create(
        snapshot_id=uuid4(),
        relative_path=PurePosixPath("src/main.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    assert first.id != second.id


def test_source_file_rejects_negative_size() -> None:
    with pytest.raises(ValueError):
        SourceFile.create(
            snapshot_id=uuid4(),
            relative_path=PurePosixPath("src/main.py"),
            language=ProgrammingLanguage.PYTHON,
            size_bytes=-1,
            content_hash="a" * 64,
        )


def test_source_file_rejects_invalid_content_hash() -> None:
    with pytest.raises(ValueError):
        SourceFile.create(
            snapshot_id=uuid4(),
            relative_path=PurePosixPath("src/main.py"),
            language=ProgrammingLanguage.PYTHON,
            size_bytes=100,
            content_hash="not-a-valid-hash",
        )


def test_source_file_id_does_not_change_when_content_changes() -> None:
    snapshot_id = uuid4()

    first = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/main.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    second = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/main.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=200,
        content_hash="b" * 64,
    )

    assert first.id == second.id
    assert first.content_hash != second.content_hash
