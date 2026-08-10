from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from codenerva.application.graph.source_file_traversal_service import (
    SourceFileNotFoundError,
    SourceFileTraversalService,
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


def test_walk_imports_respects_depth() -> None:
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
        relative_path=PurePosixPath("src/Header.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="b" * 64,
    )

    utils_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/utils.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="c" * 64,
    )

    constants_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("src/constants.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="d" * 64,
    )

    source_file_store = InMemorySourceFileStore()
    relation_store = InMemorySourceFileRelationStore()

    source_file_store.save_many(
        (
            app_file,
            header_file,
            utils_file,
            constants_file,
        )
    )

    relation_store.save_many(
        (
            SourceFileRelation.create(
                source_file_id=app_file.id,
                target_file_id=header_file.id,
                kind=SourceFileRelationKind.IMPORTS,
            ),
            SourceFileRelation.create(
                source_file_id=header_file.id,
                target_file_id=utils_file.id,
                kind=SourceFileRelationKind.IMPORTS,
            ),
            SourceFileRelation.create(
                source_file_id=utils_file.id,
                target_file_id=constants_file.id,
                kind=SourceFileRelationKind.IMPORTS,
            ),
        )
    )

    repository = InMemoryGraphRepository(
        symbol_store=InMemorySymbolStore(),
        symbol_relation_store=InMemorySymbolRelationStore(),
        source_file_store=source_file_store,
        source_file_relation_store=relation_store,
    )

    service = SourceFileTraversalService(
        graph_repository=repository,
    )

    result = service.walk_imports(
        source_file_id=app_file.id,
        max_depth=2,
    )

    assert result.root.id == app_file.id

    assert len(result.nodes) == 2

    assert result.nodes[0].source_file.id == header_file.id
    assert result.nodes[0].depth == 1

    assert result.nodes[1].source_file.id == utils_file.id
    assert result.nodes[1].depth == 2


def test_walk_imports_avoids_cycles() -> None:
    snapshot_id = uuid4()

    first_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("first.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="a" * 64,
    )

    second_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("second.js"),
        language=ProgrammingLanguage.JAVASCRIPT,
        size_bytes=100,
        content_hash="b" * 64,
    )

    source_file_store = InMemorySourceFileStore()
    relation_store = InMemorySourceFileRelationStore()

    source_file_store.save_many(
        (
            first_file,
            second_file,
        )
    )

    relation_store.save_many(
        (
            SourceFileRelation.create(
                source_file_id=first_file.id,
                target_file_id=second_file.id,
                kind=SourceFileRelationKind.IMPORTS,
            ),
            SourceFileRelation.create(
                source_file_id=second_file.id,
                target_file_id=first_file.id,
                kind=SourceFileRelationKind.IMPORTS,
            ),
        )
    )

    service = SourceFileTraversalService(
        graph_repository=InMemoryGraphRepository(
            symbol_store=InMemorySymbolStore(),
            symbol_relation_store=InMemorySymbolRelationStore(),
            source_file_store=source_file_store,
            source_file_relation_store=relation_store,
        )
    )

    result = service.walk_imports(
        source_file_id=first_file.id,
        max_depth=10,
    )

    assert len(result.nodes) == 1
    assert result.nodes[0].source_file.id == second_file.id


def test_walk_imports_requires_source_file() -> None:
    service = SourceFileTraversalService(
        graph_repository=InMemoryGraphRepository(
            symbol_store=InMemorySymbolStore(),
            symbol_relation_store=InMemorySymbolRelationStore(),
            source_file_store=InMemorySourceFileStore(),
            source_file_relation_store=(InMemorySourceFileRelationStore()),
        )
    )

    with pytest.raises(SourceFileNotFoundError):
        service.walk_imports(
            source_file_id=uuid4(),
            max_depth=2,
        )
