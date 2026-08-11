from pathlib import Path

from codenerva.application.parsing.local_import_resolver import (
    LocalImportResolver,
)
from codenerva.application.parsing.typescript_path_alias_resolver import (
    TypeScriptPathAliasResolver,
)
from codenerva.domain.import_reference import ImportReference
from codenerva.domain.programming_language import ProgrammingLanguage
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
        typescript_path_alias_resolver: TypeScriptPathAliasResolver,
    ) -> None:
        self._local_import_resolver = local_import_resolver
        self._typescript_path_alias_resolver = typescript_path_alias_resolver

    def build(
        self,
        *,
        source_file: SourceFile,
        import_references: tuple[ImportReference, ...],
        snapshot_files: tuple[SourceFile, ...],
        repository_path: Path,
    ) -> tuple[SourceFileRelation, ...]:
        relations: list[SourceFileRelation] = []

        for reference in import_references:
            target = self._local_import_resolver.resolve(
                source_file=source_file,
                import_reference=reference,
                snapshot_files=snapshot_files,
            )

            if target is None and source_file.language in {
                ProgrammingLanguage.JAVASCRIPT,
                ProgrammingLanguage.TYPESCRIPT,
                ProgrammingLanguage.TSX,
            }:
                target = self._typescript_path_alias_resolver.resolve(
                    module=reference.module,
                    repository_path=repository_path,
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
