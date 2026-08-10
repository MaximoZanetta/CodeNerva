from dataclasses import dataclass
from uuid import UUID

from codenerva.domain.import_reference_store import ImportReferenceStore
from codenerva.domain.source_file_relation_store import (
    SourceFileRelationStore,
)
from codenerva.domain.source_file_store import SourceFileStore


class SourceFileNotFoundError(Exception):
    pass


@dataclass(frozen=True, slots=True)
class ImportResult:
    id: UUID
    module: str
    imported_name: str | None
    alias: str | None
    line: int
    resolved_source_file_id: UUID | None
    resolved_relative_path: str | None


@dataclass(frozen=True, slots=True)
class ListSourceFileImportsResult:
    source_file_id: UUID
    imports: tuple[ImportResult, ...]


class ListSourceFileImportsUseCase:
    def __init__(
        self,
        *,
        source_file_store: SourceFileStore,
        import_reference_store: ImportReferenceStore,
        source_file_relation_store: SourceFileRelationStore,
    ) -> None:
        self._source_file_store = source_file_store
        self._import_reference_store = import_reference_store
        self._source_file_relation_store = source_file_relation_store

    def execute(
        self,
        source_file_id: UUID,
    ) -> ListSourceFileImportsResult:
        source_file = self._source_file_store.get_by_id(source_file_id)

        if source_file is None:
            raise SourceFileNotFoundError(
                f"Source file with id {source_file_id} was not found."
            )

        references = self._import_reference_store.list_by_source_file_id(source_file_id)

        relations = self._source_file_relation_store.list_by_source_file_id(
            source_file_id
        )

        resolved_files = []

        for relation in relations:
            target = self._source_file_store.get_by_id(relation.target_file_id)

            if target is not None:
                resolved_files.append(target)

        results: list[ImportResult] = []

        for reference in references:
            resolved_file = None

            if reference.module.startswith("."):
                for candidate in resolved_files:
                    candidate_name = candidate.relative_path.name

                    if candidate_name in reference.module or reference.module.endswith(
                        candidate.relative_path.stem
                    ):
                        resolved_file = candidate
                        break

            results.append(
                ImportResult(
                    id=reference.id,
                    module=reference.module,
                    imported_name=reference.imported_name,
                    alias=reference.alias,
                    line=reference.line,
                    resolved_source_file_id=(
                        resolved_file.id if resolved_file is not None else None
                    ),
                    resolved_relative_path=(
                        str(resolved_file.relative_path)
                        if resolved_file is not None
                        else None
                    ),
                )
            )

        return ListSourceFileImportsResult(
            source_file_id=source_file_id,
            imports=tuple(results),
        )
