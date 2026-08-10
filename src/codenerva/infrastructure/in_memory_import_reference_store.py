from uuid import UUID

from codenerva.domain.import_reference import ImportReference
from codenerva.domain.import_reference_store import ImportReferenceStore


class InMemoryImportReferenceStore(ImportReferenceStore):
    def __init__(self) -> None:
        self._references: dict[UUID, ImportReference] = {}

    def save_many(
        self,
        references: tuple[ImportReference, ...],
    ) -> None:
        for reference in references:
            self._references[reference.id] = reference

    def list_by_source_file_id(
        self,
        source_file_id: UUID,
    ) -> tuple[ImportReference, ...]:
        return tuple(
            sorted(
                (
                    reference
                    for reference in self._references.values()
                    if reference.source_file_id == source_file_id
                ),
                key=lambda reference: (
                    reference.line,
                    reference.module,
                    reference.imported_name or "",
                ),
            )
        )
