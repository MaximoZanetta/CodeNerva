import pytest
from tree_sitter import Parser

from codenerva.application.parsing.parser_registry import (
    ParserNotAvailableError,
    ParserRegistry,
)
from codenerva.domain.programming_language import ProgrammingLanguage


@pytest.mark.parametrize(
    "language",
    [
        ProgrammingLanguage.PYTHON,
        ProgrammingLanguage.JAVASCRIPT,
        ProgrammingLanguage.TYPESCRIPT,
        ProgrammingLanguage.TSX,
    ],
)
def test_registry_returns_supported_parser(
    language: ProgrammingLanguage,
) -> None:
    registry = ParserRegistry()

    parser = registry.get(language)

    assert isinstance(parser, Parser)


def test_registry_raises_when_parser_is_not_available() -> None:
    registry = ParserRegistry()

    with pytest.raises(ParserNotAvailableError):
        registry.get(ProgrammingLanguage.RUST)
