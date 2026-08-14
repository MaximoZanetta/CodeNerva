from datetime import UTC
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from codenerva.domain.analysis_job import (
    AnalysisJob,
    AnalysisJobStatus,
)
from codenerva.domain.analysis_job_store import AnalysisJobStore
from codenerva.infrastructure.database.models.analysis_job_model import (
    AnalysisJobModel,
)


class PostgresAnalysisJobStore(AnalysisJobStore):
    def __init__(
        self,
        *,
        session_factory: sessionmaker[Session],
    ) -> None:
        self._session_factory = session_factory

    def save(
        self,
        job: AnalysisJob,
    ) -> None:
        with self._session_factory() as session:
            model = AnalysisJobModel(
                id=job.id,
                snapshot_id=job.snapshot_id,
                status=job.status.value,
                progress=job.progress,
                error_message=job.error_message,
                created_at=job.created_at,
                updated_at=job.updated_at,
            )

            session.merge(model)
            session.commit()

    def get_by_id(
        self,
        job_id: UUID,
    ) -> AnalysisJob | None:
        with self._session_factory() as session:
            model = session.get(
                AnalysisJobModel,
                job_id,
            )

            if model is None:
                return None

            return self._to_domain(model)

    def get_by_snapshot_id(
        self,
        snapshot_id: UUID,
    ) -> AnalysisJob | None:
        with self._session_factory() as session:
            statement = (
                select(AnalysisJobModel)
                .where(AnalysisJobModel.snapshot_id == snapshot_id)
                .order_by(AnalysisJobModel.created_at.desc())
                .limit(1)
            )

            model = session.scalar(statement)

            if model is None:
                return None

            return self._to_domain(model)

    def _to_domain(
        self,
        model: AnalysisJobModel,
    ) -> AnalysisJob:
        created_at = model.created_at
        updated_at = model.updated_at

        if created_at.tzinfo is None:
            created_at = created_at.replace(
                tzinfo=UTC,
            )

        if updated_at.tzinfo is None:
            updated_at = updated_at.replace(
                tzinfo=UTC,
            )

        return AnalysisJob(
            id=model.id,
            snapshot_id=model.snapshot_id,
            status=AnalysisJobStatus(model.status),
            progress=model.progress,
            error_message=model.error_message,
            created_at=created_at,
            updated_at=updated_at,
        )
