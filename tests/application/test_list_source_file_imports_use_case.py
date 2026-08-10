from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from codenerva.application.parsing.list_source_file_imports import (
    ListSourceFileImportsUseCase,
    SourceFileNotFoundError,
)
from codenerva.domain.import_reference import ImportReference
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelation,
    SourceFileRelationKind,
)
from codenerva.infrastructure.in_memory_import_reference_store import (
    InMemoryImportReferenceStore,
)
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)


def test_list_source_file_imports() -> None:
    snapshot_id = uuid4()

    source_file_store = InMemorySourceFileStore()
    import_reference_store = InMemoryImportReferenceStore()
    relation_store = InMemorySourceFileRelationStore()

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

    source_file_store.save_many(
        (
            app_file,
            header_file,
        )
    )

    reference = ImportReference.create(
        source_file_id=app_file.id,
        module="./components/Header.js",
        imported_name="default",
        alias="Header",
        line=1,
    )

    import_reference_store.save_many((reference,))

    relation = SourceFileRelation.create(
        source_file_id=app_file.id,
        target_file_id=header_file.id,
        kind=SourceFileRelationKind.IMPORTS,
    )

    relation_store.save_many((relation,))

    use_case = ListSourceFileImportsUseCase(
        source_file_store=source_file_store,
        import_reference_store=import_reference_store,
        source_file_relation_store=relation_store,
    )

    result = use_case.execute(app_file.id)

    assert len(result.imports) == 1
    assert result.imports[0].module == "./components/Header.js"
    assert result.imports[0].resolved_source_file_id == header_file.id
    assert result.imports[0].resolved_relative_path == "src/components/Header.js"


def test_list_source_file_imports_requires_source_file() -> None:
    use_case = ListSourceFileImportsUseCase(
        source_file_store=InMemorySourceFileStore(),
        import_reference_store=InMemoryImportReferenceStore(),
        source_file_relation_store=InMemorySourceFileRelationStore(),
    )

    with pytest.raises(SourceFileNotFoundError):
        use_case.execute(uuid4())
