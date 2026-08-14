from dataclasses import replace
from datetime import datetime
from uuid import UUID

from codenerva.application.analysis.codenerva_analysis_pipeline import (
    CodeNervaAnalysisPipeline,
)
from codenerva.domain.snapshot import (
    Snapshot,
    SnapshotStatus,
)
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
)


class FakeDiscoverSnapshotFilesUseCase:
    def __init__(self) -> None:
        self.calls: list[UUID] = []

    def execute(
        self,
        snapshot_id: UUID,
    ) -> None:
        self.calls.append(snapshot_id)


class FakeAnalyzeSnapshotUseCase:
    def __init__(self) -> None:
        self.calls: list[UUID] = []

    def execute(
        self,
        snapshot_id: UUID,
    ) -> None:
        self.calls.append(snapshot_id)


class FakeIndexSnapshotUseCase:
    def __init__(self) -> None:
        self.calls: list[UUID] = []

    def execute(
        self,
        *,
        snapshot_id: UUID,
    ) -> None:
        self.calls.append(snapshot_id)


class FakeIncrementalIndexSnapshotUseCase:
    def __init__(self) -> None:
        self.calls: list[tuple[UUID, UUID]] = []

    def execute(
        self,
        *,
        previous_snapshot_id: UUID,
        current_snapshot_id: UUID,
    ) -> None:
        self.calls.append(
            (
                previous_snapshot_id,
                current_snapshot_id,
            )
        )


def _create_snapshot(
    *,
    repository_id: UUID,
    commit_sha: str,
    status: SnapshotStatus,
    created_at: datetime,
) -> Snapshot:
    snapshot = Snapshot.create(
        repository_id=repository_id,
        commit_sha=commit_sha,
        branch="main",
        remote_url="https://github.com/example/repo",
    )

    return replace(
        snapshot,
        status=status,
        created_at=created_at,
    )


def _build_pipeline(
    *,
    snapshot_store: InMemorySnapshotStore,
) -> tuple[
    CodeNervaAnalysisPipeline,
    FakeDiscoverSnapshotFilesUseCase,
    FakeAnalyzeSnapshotUseCase,
    FakeIndexSnapshotUseCase,
    FakeIncrementalIndexSnapshotUseCase,
]:
    discover = FakeDiscoverSnapshotFilesUseCase()
    analyze = FakeAnalyzeSnapshotUseCase()
    index = FakeIndexSnapshotUseCase()
    incremental = FakeIncrementalIndexSnapshotUseCase()

    pipeline = CodeNervaAnalysisPipeline(
        snapshot_store=snapshot_store,
        discover_snapshot_files_use_case=discover,
        analyze_snapshot_use_case=analyze,
        index_snapshot_use_case=index,
        incremental_index_snapshot_use_case=incremental,
    )

    return (
        pipeline,
        discover,
        analyze,
        index,
        incremental,
    )
