from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.import_reference import ImportReference
from codenerva.infrastructure.database.base import Base
from codenerva.infrastructure.database.models.import_reference_model import (
    ImportReferenceModel,
)
from codenerva.infrastructure.database.postgres_import_reference_store import (
    PostgresImportReferenceStore,
)


def test_postgres_import_reference_store_round_trip() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
    )

    _ = ImportReferenceModel

    Base.metadata.create_all(
        bind=engine,
    )

    session_factory = sessionmaker[Session](
        bind=engine,
        expire_on_commit=False,
    )

    store = PostgresImportReferenceStore(
        session_factory=session_factory,
    )

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
        module="google.generativeai",
        imported_name=None,
        alias="genai",
        line=2,
    )

    store.save_many(
        (
            first,
            second,
        )
    )

    listed = store.list_by_source_file_id(source_file_id)

    assert listed == (
        first,
        second,
    )
