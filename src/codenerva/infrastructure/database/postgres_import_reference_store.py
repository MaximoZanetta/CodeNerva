from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.import_reference import ImportReference
from codenerva.domain.import_reference_store import (
    ImportReferenceStore,
)
from codenerva.infrastructure.database.models.import_reference_model import (
    ImportReferenceModel,
)


class PostgresImportReferenceStore(ImportReferenceStore):
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def save_many(
        self,
        references: tuple[ImportReference, ...],
    ) -> None:
        if not references:
            return

        with self._session_factory() as session:
            for reference in references:
                model = ImportReferenceModel(
                    id=reference.id,
                    source_file_id=reference.source_file_id,
                    module=reference.module,
                    imported_name=reference.imported_name,
                    alias=reference.alias,
                    line=reference.line,
                )

                session.merge(model)

            session.commit()

    def list_by_source_file_id(
        self,
        source_file_id: UUID,
    ) -> tuple[ImportReference, ...]:
        with self._session_factory() as session:
            statement = (
                select(ImportReferenceModel)
                .where(ImportReferenceModel.source_file_id == source_file_id)
                .order_by(
                    ImportReferenceModel.line,
                    ImportReferenceModel.module,
                )
            )

            models = session.scalars(statement).all()

            return tuple(self._to_domain(model) for model in models)

    def _to_domain(
        self,
        model: ImportReferenceModel,
    ) -> ImportReference:
        return ImportReference(
            id=model.id,
            source_file_id=model.source_file_id,
            module=model.module,
            imported_name=model.imported_name,
            alias=model.alias,
            line=model.line,
        )

    def delete_by_source_file_ids(
        self,
        source_file_ids: tuple[UUID, ...],
    ) -> int:
        if not source_file_ids:
            return 0

        with self._session_factory() as session:
            statement = delete(ImportReferenceModel).where(
                ImportReferenceModel.source_file_id.in_(source_file_ids)
            )

            result = session.execute(statement)
            session.commit()

            return result.rowcount or 0
