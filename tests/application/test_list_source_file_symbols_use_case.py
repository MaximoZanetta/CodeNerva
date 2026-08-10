from pathlib import PurePosixPath
from uuid import uuid4

import pytest

from codenerva.application.parsing.list_source_file_symbols import (
    ListSourceFileSymbolsUseCase,
    SourceFileNotFoundError,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)
from codenerva.infrastructure.in_memory_symbol_store import (
    InMemorySymbolStore,
)


def test_list_source_file_symbols() -> None:
    source_file_store = InMemorySourceFileStore()
    symbol_store = InMemorySymbolStore()

    source_file = SourceFile.create(
        snapshot_id=uuid4(),
        relative_path=PurePosixPath("service.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    source_file_store.save_many((source_file,))

    symbol = Symbol.create(
        source_file_id=source_file.id,
        name="login",
        qualified_name="login",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    symbol_store.save_many((symbol,))

    use_case = ListSourceFileSymbolsUseCase(
        source_file_store=source_file_store,
        symbol_store=symbol_store,
    )

    result = use_case.execute(source_file.id)

    assert result.source_file_id == source_file.id
    assert len(result.symbols) == 1
    assert result.symbols[0].name == "login"


def test_list_source_file_symbols_requires_source_file() -> None:
    use_case = ListSourceFileSymbolsUseCase(
        source_file_store=InMemorySourceFileStore(),
        symbol_store=InMemorySymbolStore(),
    )

    with pytest.raises(SourceFileNotFoundError):
        use_case.execute(uuid4())
