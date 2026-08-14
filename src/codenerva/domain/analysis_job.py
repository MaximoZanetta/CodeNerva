from dataclasses import dataclass, replace
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class AnalysisJobStatus(StrEnum):
    QUEUED = "QUEUED"
    DISCOVERING = "DISCOVERING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class AnalysisJob:
    id: UUID
    snapshot_id: UUID
    status: AnalysisJobStatus
    progress: int
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def create(
        cls,
        *,
        snapshot_id: UUID,
    ) -> "AnalysisJob":
        now = datetime.now(UTC)

        return cls(
            id=uuid4(),
            snapshot_id=snapshot_id,
            status=AnalysisJobStatus.QUEUED,
            progress=0,
            error_message=None,
            created_at=now,
            updated_at=now,
        )

    def transition_to(
        self,
        *,
        status: AnalysisJobStatus,
        progress: int,
    ) -> "AnalysisJob":
        if not 0 <= progress <= 100:
            raise ValueError("progress must be between 0 and 100.")

        if self.status in {
            AnalysisJobStatus.READY,
            AnalysisJobStatus.FAILED,
        }:
            raise ValueError(
                "A finished analysis job cannot transition to another status."
            )

        if progress < self.progress:
            raise ValueError("Analysis job progress cannot decrease.")

        return replace(
            self,
            status=status,
            progress=progress,
            error_message=None,
            updated_at=datetime.now(UTC),
        )

    def mark_failed(
        self,
        *,
        error_message: str,
    ) -> "AnalysisJob":
        normalized_error = error_message.strip()

        if not normalized_error:
            raise ValueError("error_message cannot be blank.")

        if self.status is AnalysisJobStatus.READY:
            raise ValueError("A ready analysis job cannot be marked as failed.")

        return replace(
            self,
            status=AnalysisJobStatus.FAILED,
            error_message=normalized_error,
            updated_at=datetime.now(UTC),
        )

    def mark_ready(
        self,
    ) -> "AnalysisJob":
        return self.transition_to(
            status=AnalysisJobStatus.READY,
            progress=100,
        )
