from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from codenerva.application.graph.source_file_query_service import (
    SourceFileNotFoundError,
    SourceFileQueryService,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.source_file_relation import (
    SourceFileRelation,
    SourceFileRelationKind,
)
from codenerva.infrastructure.in_memory_graph_repository import (
    InMemoryGraphRepository,
)
from codenerva.infrastructure.in_memory_source_file_relation_store import (
    InMemorySourceFileRelationStore,
)
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)
from codenerva.infrastructure.in_memory_symbol_relation_store import (
    InMemorySymbolRelationStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)


def test_get_source_file_neighbors() -> None:
    snapshot_id = uuid4()

    source_file_store = InMemorySourceFileStore()
    source_file_relation_store = InMemorySourceFileRelationStore()

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

    main_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/main.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="c" * 64,
    )

    source_file_store.save_many(
        (
            app_file,
            header_file,
            main_file,
        )
    )

    source_file_relation_store.save_many(
        (
            SourceFileRelation.create(
                source_file_id=app_file.id,
                target_file_id=header_file.id,
                kind=SourceFileRelationKind.IMPORTS,
            ),
            SourceFileRelation.create(
                source_file_id=main_file.id,
                target_file_id=app_file.id,
                kind=SourceFileRelationKind.IMPORTS,
            ),
        )
    )

    graph_repository = InMemoryGraphRepository(
        symbol_store=InMemorySymbolStore(),
        symbol_relation_store=InMemorySymbolRelationStore(),
        source_file_store=source_file_store,
        source_file_relation_store=source_file_relation_store,
    )

    service = SourceFileQueryService(
        graph_repository=graph_repository,
    )

    result = service.get_source_file_neighbors(app_file.id)

    assert result.source_file.id == app_file.id

    assert len(result.imports) == 1
    assert result.imports[0].id == header_file.id

    assert len(result.imported_by) == 1
    assert result.imported_by[0].id == main_file.id


def test_get_source_file_neighbors_requires_file() -> None:
    service = SourceFileQueryService(
        graph_repository=InMemoryGraphRepository(
            symbol_store=InMemorySymbolStore(),
            symbol_relation_store=InMemorySymbolRelationStore(),
            source_file_store=InMemorySourceFileStore(),
            source_file_relation_store=(InMemorySourceFileRelationStore()),
        )
    )

    with pytest.raises(SourceFileNotFoundError):
        service.get_source_file_neighbors(uuid4())
