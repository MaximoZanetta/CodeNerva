from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.parsing.build_source_file_relations import (
    BuildSourceFileRelationsService,
)
from codenerva.application.parsing.local_import_resolver import (
    LocalImportResolver,
)
from codenerva.domain.import_reference import ImportReference
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelationKind,
)


def test_build_import_relation_between_files() -> None:
    snapshot_id = uuid4()

    app_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/App.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="a" * 64,
    )

    header_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/components/Header.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="b" * 64,
    )

    reference = ImportReference.create(
        source_file_id=app_file.id,
        module="./components/Header.js",
        imported_name="default",
        alias="Header",
        line=1,
    )

    service = BuildSourceFileRelationsService(
        local_import_resolver=LocalImportResolver(),
    )

    relations = service.build(
        source_file=app_file,
        import_references=(reference,),
        snapshot_files=(
            app_file,
            header_file,
        ),
    )

    assert len(relations) == 1

    relation = relations[0]

    assert relation.source_file_id == app_file.id
    assert relation.target_file_id == header_file.id
    assert relation.kind is SourceFileRelationKind.IMPORTS
