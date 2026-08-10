from codenerva.application.parsing.local_import_resolver import (
    LocalImportResolver,
)
from codenerva.domain.import_reference import ImportReference
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelation,
    SourceFileRelationKind,
)


class BuildSourceFileRelationsService:
    def __init__(
        self,
        *,
        local_import_resolver: LocalImportResolver,
    ) -> None:
        self._local_import_resolver = local_import_resolver

    def build(
        self,
        *,
        source_file: SourceFile,
        import_references: tuple[ImportReference, ...],
        snapshot_files: tuple[SourceFile, ...],
    ) -> tuple[SourceFileRelation, ...]:
        relations: list[SourceFileRelation] = []

        for reference in import_references:
            target = self._local_import_resolver.resolve(
                source_file=source_file,
                import_reference=reference,
                snapshot_files=snapshot_files,
            )

            if target is None:
                continue

            relations.append(
                SourceFileRelation.create(
                    source_file_id=source_file.id,
                    target_file_id=target.id,
                    kind=SourceFileRelationKind.IMPORTS,
                )
            )

        return tuple(relations)
