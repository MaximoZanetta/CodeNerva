from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.parsing.local_import_resolver import (
    LocalImportResolver,
)
from codenerva.domain.import_reference import ImportReference
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile


def test_resolve_javascript_relative_import() -> None:
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

    resolver = LocalImportResolver()

    result = resolver.resolve(
        source_file=app_file,
        import_reference=reference,
        snapshot_files=(
            app_file,
            header_file,
        ),
    )

    assert result is not None
    assert result.id == header_file.id


def test_resolve_python_relative_import() -> None:
    snapshot_id = uuid4()

    source_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/api/routes.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    service_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/api/service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="b" * 64,
    )

    reference = ImportReference.create(
        source_file_id=source_file.id,
        module=".service",
        imported_name="UserService",
        alias=None,
        line=1,
    )

    resolver = LocalImportResolver()

    result = resolver.resolve(
        source_file=source_file,
        import_reference=reference,
        snapshot_files=(
            source_file,
            service_file,
        ),
    )

    assert result is not None
    assert result.id == service_file.id
