from pathlib import PurePosixPath
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_store import SourceFileStore
from codenerva.infrastructure.database.models.source_file_model import (
    SourceFileModel,
)


class PostgresSourceFileStore(SourceFileStore):
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def save_many(
        self,
        source_files: tuple[SourceFile, ...],
    ) -> None:
        if not source_files:
            return

        with self._session_factory() as session:
            for source_file in source_files:
                model = SourceFileModel(
                    id=source_file.id,
                    snapshot_id=source_file.snapshot_id,
                    relative_path=source_file.relative_path.as_posix(),
                    language=source_file.language.value,
                    size_bytes=source_file.size_bytes,
                    content_hash=source_file.content_hash,
                )

                session.merge(model)

            session.commit()

    def list_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> tuple[SourceFile, ...]:
        with self._session_factory() as session:
            statement = (
                select(SourceFileModel)
                .where(SourceFileModel.snapshot_id == snapshot_id)
                .order_by(SourceFileModel.relative_path)
            )

            models = session.scalars(statement).all()

            return tuple(self._to_domain(model) for model in models)

    def get_by_id(
        self,
        source_file_id: UUID,
    ) -> SourceFile | None:
        with self._session_factory() as session:
            model = session.get(
                SourceFileModel,
                source_file_id,
            )

            if model is None:
                return None

            return self._to_domain(model)

    def _to_domain(
        self,
        model: SourceFileModel,
    ) -> SourceFile:
        return SourceFile(
            id=model.id,
            snapshot_id=model.snapshot_id,
            relative_path=PurePosixPath(model.relative_path),
            language=ProgrammingLanguage(model.language),
            size_bytes=model.size_bytes,
            content_hash=model.content_hash,
        )

    def delete_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> int:
        with self._session_factory() as session:
            statement = delete(SourceFileModel).where(
                SourceFileModel.snapshot_id == snapshot_id
            )

            result = session.execute(statement)
            session.commit()

            return result.rowcount or 0
