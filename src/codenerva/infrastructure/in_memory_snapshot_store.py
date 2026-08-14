from uuid import UUID

from codenerva.domain.snapshot import Snapshot
from codenerva.domain.snapshot_store import SnapshotStore


class InMemorySnapshotStore(SnapshotStore):
    def __init__(self) -> None:
        self._snapshots: dict[UUID, Snapshot] = {}

    def save(self, snapshot: Snapshot) -> None:
        self._snapshots[snapshot.id] = snapshot

    def get_by_id(self, snapshot_id: UUID) -> Snapshot | None:
        return self._snapshots.get(snapshot_id)

    def get_by_repository_and_commit(
        self,
        repository_id: UUID,
        commit_sha: str,
    ) -> Snapshot | None:
        return next(
            (
                snapshot
                for snapshot in self._snapshots.values()
                if snapshot.repository_id == repository_id
                and snapshot.commit_sha == commit_sha
            ),
            None,
        )

    def delete(
        self,
        snapshot_id: UUID,
    ) -> bool:
        if snapshot_id not in self._snapshots:
            return False

        del self._snapshots[snapshot_id]

        return True

    def list_by_repository_id(
        self,
        repository_id: UUID,
    ) -> tuple[Snapshot, ...]:
        snapshots = tuple(
            snapshot
            for snapshot in self._snapshots.values()
            if snapshot.repository_id == repository_id
        )

        return tuple(
            sorted(
                snapshots,
                key=lambda snapshot: snapshot.created_at,
            )
        )
