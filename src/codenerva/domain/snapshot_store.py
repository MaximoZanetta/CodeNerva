from typing import Protocol
from uuid import UUID

from codenerva.domain.snapshot import Snapshot


class SnapshotStore(Protocol):
    def save(self, snapshot: Snapshot) -> None: ...

    def get_by_id(self, snapshot_id: UUID) -> Snapshot | None: ...

    def get_by_repository_and_commit(
        self,
        repository_id: UUID,
        commit_sha: str,
    ) -> Snapshot | None: ...

    def delete(
        self,
        snapshot_id: UUID,
    ) -> bool: ...
