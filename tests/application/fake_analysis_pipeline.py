from uuid import UUID


class FakeAnalysisPipeline:
    def __init__(
        self,
        *,
        fail_at: str | None = None,
    ) -> None:
        self.fail_at = fail_at
        self.calls: list[str] = []
        self.snapshot_ids: list[UUID] = []

    def discover(
        self,
        *,
        snapshot_id: UUID,
    ) -> None:
        self._execute_stage(
            stage="discover",
            snapshot_id=snapshot_id,
        )

    def process(
        self,
        *,
        snapshot_id: UUID,
    ) -> None:
        self._execute_stage(
            stage="process",
            snapshot_id=snapshot_id,
        )

    def _execute_stage(
        self,
        *,
        stage: str,
        snapshot_id: UUID,
    ) -> None:
        self.calls.append(stage)
        self.snapshot_ids.append(snapshot_id)

        if self.fail_at == stage:
            raise RuntimeError(f"{stage} failed.")
