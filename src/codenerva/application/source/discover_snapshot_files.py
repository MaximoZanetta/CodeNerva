from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from codenerva.application.source.file_discovery import (
    FileDiscoveryService,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.snapshot_store import SnapshotStore
from codenerva.domain.source_file_store import SourceFileStore


class SnapshotNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class LanguageSummary:
    language: ProgrammingLanguage
    file_count: int
    total_bytes: int


@dataclass(frozen=True, slots=True)
class DiscoverSnapshotFilesResult:
    snapshot_id: UUID
    total_files: int
    ignored_count: int
    languages: tuple[LanguageSummary, ...]


class DiscoverSnapshotFilesUseCase:
    def __init__(
        self,
        *,
        snapshot_store: SnapshotStore,
        source_file_store: SourceFileStore,
        file_discovery_service: FileDiscoveryService,
        storage_root: Path,
    ) -> None:
        self._snapshot_store = snapshot_store
        self._source_file_store = source_file_store
        self._file_discovery_service = file_discovery_service
        self._storage_root = storage_root

    def execute(
        self,
        snapshot_id: UUID,
    ) -> DiscoverSnapshotFilesResult:
        snapshot = self._snapshot_store.get_by_id(snapshot_id)

        if snapshot is None:
            raise SnapshotNotFoundError(
                f"Snapshot with id {snapshot_id} was not found."
            )

        repository_path = (
            self._storage_root / "repositories" / str(snapshot.repository_id)
        )

        discovery_result = self._file_discovery_service.discover(
            snapshot_id=snapshot.id,
            repository_path=repository_path,
        )
        self._source_file_store.save_many(discovery_result.files)

        language_totals: dict[
            ProgrammingLanguage,
            tuple[int, int],
        ] = {}

        for source_file in discovery_result.files:
            file_count, total_bytes = language_totals.get(
                source_file.language,
                (0, 0),
            )

            language_totals[source_file.language] = (
                file_count + 1,
                total_bytes + source_file.size_bytes,
            )

        languages = tuple(
            LanguageSummary(
                language=language,
                file_count=file_count,
                total_bytes=total_bytes,
            )
            for language, (
                file_count,
                total_bytes,
            ) in sorted(
                language_totals.items(),
                key=lambda item: item[0].value,
            )
        )

        return DiscoverSnapshotFilesResult(
            snapshot_id=snapshot.id,
            total_files=len(discovery_result.files),
            ignored_count=discovery_result.ignored_count,
            languages=languages,
        )
