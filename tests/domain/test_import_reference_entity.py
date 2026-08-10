from uuid import uuid4

import pytest

from codenerva.domain.import_reference import ImportReference


def test_create_import_reference() -> None:
    source_file_id = uuid4()

    reference = ImportReference.create(
        source_file_id=source_file_id,
        module="flask",
        imported_name="Flask",
        alias=None,
        line=1,
    )

    assert reference.source_file_id == source_file_id
    assert reference.module == "flask"
    assert reference.imported_name == "Flask"
    assert reference.alias is None
    assert reference.line == 1


def test_import_reference_id_is_deterministic() -> None:
    source_file_id = uuid4()

    first = ImportReference.create(
        source_file_id=source_file_id,
        module="flask",
        imported_name="Flask",
        alias=None,
        line=1,
    )

    second = ImportReference.create(
        source_file_id=source_file_id,
        module="flask",
        imported_name="Flask",
        alias=None,
        line=1,
    )

    assert first.id == second.id


def test_import_reference_rejects_empty_module() -> None:
    with pytest.raises(ValueError):
        ImportReference.create(
            source_file_id=uuid4(),
            module="",
            imported_name=None,
            alias=None,
            line=1,
        )
