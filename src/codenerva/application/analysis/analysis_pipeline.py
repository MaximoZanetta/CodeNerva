from typing import Protocol
from uuid import UUID


class AnalysisPipeline(Protocol):
    def discover(
        self,
        *,
        snapshot_id: UUID,
    ) -> None: ...

    def process(
        self,
        *,
        snapshot_id: UUID,
    ) -> None: ...
