from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from codenerva.application.parsing.list_source_file_relations import (
    ListSourceFileRelationsUseCase,
    SourceFileNotFoundError,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelation,
    SourceFileRelationKind,
)
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)


def test_list_source_file_relations() -> None:
    snapshot_id = uuid4()

    source_file_store = InMemorySourceFileStore()
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

    relation = SourceFileRelation.create(
        source_file_id=app_file.id,
        target_file_id=header_file.id,
        kind=SourceFileRelationKind.IMPORTS,
    )

    relation_store.save_many((relation,))

    use_case = ListSourceFileRelationsUseCase(
        source_file_store=source_file_store,
        source_file_relation_store=relation_store,
    )

    result = use_case.execute(app_file.id)

    assert len(result.relations) == 1
    assert result.relations[0].kind is SourceFileRelationKind.IMPORTS
    assert result.relations[0].target_source_file_id == header_file.id
    assert result.relations[0].target_relative_path == "src/components/Header.js"


def test_list_source_file_relations_requires_source_file() -> None:
    use_case = ListSourceFileRelationsUseCase(
        source_file_store=InMemorySourceFileStore(),
        source_file_relation_store=InMemorySourceFileRelationStore(),
    )

    with pytest.raises(SourceFileNotFoundError):
        use_case.execute(uuid4())
