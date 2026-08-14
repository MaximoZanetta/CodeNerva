from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class SnapshotStatus(StrEnum):
    PENDING = "PENDING"
    READY = "READY"
    FAILED = "FAILED"


@dataclass(frozen=True, slots=True)
class Snapshot:
    id: UUID
    repository_id: UUID
    commit_sha: str
    branch: str | None
    remote_url: str
    status: SnapshotStatus
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @classmethod
    def create(
        cls,
        *,
        repository_id: UUID,
        commit_sha: str,
        branch: str | None,
        remote_url: str,
    ) -> "Snapshot":
        normalized_commit_sha = commit_sha.strip().lower()

        if len(normalized_commit_sha) != 40:
            raise ValueError("Commit SHA must contain exactly 40 characters.")

        if not all(
            character in "0123456789abcdef" for character in normalized_commit_sha
        ):
            raise ValueError("Commit SHA must be hexadecimal.")

        normalized_branch = branch.strip() if branch and branch.strip() else None

        normalized_remote_url = remote_url.strip()

        if not normalized_remote_url:
            raise ValueError("Snapshot remote URL cannot be empty.")

        return cls(
            id=uuid4(),
            repository_id=repository_id,
            commit_sha=normalized_commit_sha,
            branch=normalized_branch,
            remote_url=normalized_remote_url,
            status=SnapshotStatus.PENDING,
        )

    def mark_ready(self) -> "Snapshot":
        return Snapshot(
            id=self.id,
            repository_id=self.repository_id,
            commit_sha=self.commit_sha,
            branch=self.branch,
            remote_url=self.remote_url,
            status=SnapshotStatus.READY,
            created_at=self.created_at,
        )
