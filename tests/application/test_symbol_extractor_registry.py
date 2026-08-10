import pytest

from codenerva.application.parsing.javascript_symbol_extractor import (
    JavaScriptSymbolExtractor,
)
from codenerva.application.parsing.python_symbol_extractor import (
    PythonSymbolExtractor,
)
from codenerva.application.parsing.symbol_extractor_registry import (
    SymbolExtractorNotAvailableError,
    SymbolExtractorRegistry,
)
from codenerva.application.parsing.typescript_symbol_extractor import (
    TypeScriptSymbolExtractor,
)
from codenerva.domain.programming_language import ProgrammingLanguage


@pytest.mark.parametrize(
    ("language", "extractor_type"),
    [
        (
            ProgrammingLanguage.PYTHON,
            PythonSymbolExtractor,
        ),
        (
            ProgrammingLanguage.JAVASCRIPT,
            JavaScriptSymbolExtractor,
        ),
        (
            ProgrammingLanguage.TYPESCRIPT,
            TypeScriptSymbolExtractor,
        ),
        (
            ProgrammingLanguage.TSX,
            TypeScriptSymbolExtractor,
        ),
    ],
)
def test_registry_returns_supported_extractor(
    language: ProgrammingLanguage,
    extractor_type: type,
) -> None:
    registry = SymbolExtractorRegistry()

    extractor = registry.get(language)

    assert isinstance(extractor, extractor_type)


def test_registry_raises_for_unsupported_language() -> None:
    registry = SymbolExtractorRegistry()

    with pytest.raises(SymbolExtractorNotAvailableError):
        registry.get(ProgrammingLanguage.RUST)
