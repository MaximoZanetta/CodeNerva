from typing import Protocol
from uuid import UUID

from codenerva.domain.import_reference import ImportReference


class ImportReferenceStore(Protocol):
    def save_many(
        self,
        references: tuple[ImportReference, ...],
    ) -> None: ...

    def list_by_source_file_id(
        self,
        source_file_id: UUID,
    ) -> tuple[ImportReference, ...]: ...
