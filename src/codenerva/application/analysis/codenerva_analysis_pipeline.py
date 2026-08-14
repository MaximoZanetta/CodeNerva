from uuid import UUID

from codenerva.application.embeddings.index_snapshot import (
    IndexSnapshotUseCase,
)
from codenerva.application.parsing.analyze_snapshot import (
    AnalyzeSnapshotUseCase,
)
from codenerva.application.snapshots.incremental_index_snapshot import (
    IncrementalIndexSnapshotUseCase,
)
from codenerva.application.source.discover_snapshot_files import (
    DiscoverSnapshotFilesUseCase,
)
from codenerva.domain.snapshot import (
    Snapshot,
    SnapshotStatus,
)
from codenerva.domain.snapshot_store import SnapshotStore


class AnalysisSnapshotNotFoundError(Exception):
    pass


class CodeNervaAnalysisPipeline:
    def __init__(
        self,
        *,
        snapshot_store: SnapshotStore,
        discover_snapshot_files_use_case: DiscoverSnapshotFilesUseCase,
        analyze_snapshot_use_case: AnalyzeSnapshotUseCase,
        index_snapshot_use_case: IndexSnapshotUseCase,
        incremental_index_snapshot_use_case: IncrementalIndexSnapshotUseCase,
    ) -> None:
        self._snapshot_store = snapshot_store
        self._discover_snapshot_files_use_case = discover_snapshot_files_use_case
        self._analyze_snapshot_use_case = analyze_snapshot_use_case
        self._index_snapshot_use_case = index_snapshot_use_case
        self._incremental_index_snapshot_use_case = incremental_index_snapshot_use_case

    def discover(
        self,
        *,
        snapshot_id: UUID,
    ) -> None:
        self._discover_snapshot_files_use_case.execute(
            snapshot_id=snapshot_id,
        )

    def process(
        self,
        *,
        snapshot_id: UUID,
    ) -> None:
        current_snapshot = self._snapshot_store.get_by_id(snapshot_id)

        if current_snapshot is None:
            raise AnalysisSnapshotNotFoundError(
                f"Snapshot with id {snapshot_id} was not found."
            )

        previous_snapshot = self._find_previous_ready_snapshot(
            current_snapshot=current_snapshot,
        )

        if previous_snapshot is None:
            self._run_full_processing(
                snapshot_id=snapshot_id,
            )
            return

        self._run_incremental_processing(
            previous_snapshot_id=previous_snapshot.id,
            current_snapshot_id=snapshot_id,
        )

    def _run_full_processing(
        self,
        *,
        snapshot_id: UUID,
    ) -> None:
        self._analyze_snapshot_use_case.execute(
            snapshot_id=snapshot_id,
        )

        self._index_snapshot_use_case.execute(
            snapshot_id=snapshot_id,
        )

    def _run_incremental_processing(
        self,
        *,
        previous_snapshot_id: UUID,
        current_snapshot_id: UUID,
    ) -> None:
        self._incremental_index_snapshot_use_case.execute(
            previous_snapshot_id=previous_snapshot_id,
            current_snapshot_id=current_snapshot_id,
        )

    def _find_previous_ready_snapshot(
        self,
        *,
        current_snapshot: Snapshot,
    ) -> Snapshot | None:
        repository_snapshots = self._snapshot_store.list_by_repository_id(
            current_snapshot.repository_id
        )

        candidates = tuple(
            snapshot
            for snapshot in repository_snapshots
            if (
                snapshot.id != current_snapshot.id
                and snapshot.status is SnapshotStatus.READY
                and snapshot.created_at < current_snapshot.created_at
            )
        )

        if not candidates:
            return None

        return max(
            candidates,
            key=lambda snapshot: snapshot.created_at,
        )
