from uuid import uuid4

import pytest

from codenerva.domain.symbol import Symbol, SymbolKind


def test_create_symbol() -> None:
    source_file_id = uuid4()

    symbol = Symbol.create(
        source_file_id=source_file_id,
        name="AuthService",
        qualified_name="AuthService",
        kind=SymbolKind.CLASS,
        start_line=1,
        end_line=10,
    )

    assert symbol.source_file_id == source_file_id
    assert symbol.name == "AuthService"
    assert symbol.qualified_name == "AuthService"
    assert symbol.kind is SymbolKind.CLASS
    assert symbol.start_line == 1
    assert symbol.end_line == 10
    assert symbol.parent_symbol_id is None


def test_symbol_id_is_deterministic() -> None:
    source_file_id = uuid4()

    first = Symbol.create(
        source_file_id=source_file_id,
        name="login",
        qualified_name="AuthService.login",
        kind=SymbolKind.METHOD,
        start_line=5,
        end_line=8,
    )

    second = Symbol.create(
        source_file_id=source_file_id,
        name="login",
        qualified_name="AuthService.login",
        kind=SymbolKind.METHOD,
        start_line=5,
        end_line=8,
    )

    assert first.id == second.id


def test_symbol_rejects_invalid_line_range() -> None:
    with pytest.raises(ValueError):
        Symbol.create(
            source_file_id=uuid4(),
            name="login",
            qualified_name="login",
            kind=SymbolKind.FUNCTION,
            start_line=10,
            end_line=5,
        )
