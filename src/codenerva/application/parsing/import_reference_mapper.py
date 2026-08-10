from uuid import UUID

from codenerva.application.parsing.python_import_extractor import (
    ExtractedImport,
)
from codenerva.domain.import_reference import ImportReference


class ImportReferenceMapper:
    def map(
        self,
        *,
        source_file_id: UUID,
        extracted_imports: tuple[ExtractedImport, ...],
    ) -> tuple[ImportReference, ...]:
        return tuple(
            ImportReference.create(
                source_file_id=source_file_id,
                module=extracted.module,
                imported_name=extracted.imported_name,
                alias=extracted.alias,
                line=extracted.line,
            )
            for extracted in extracted_imports
        )
