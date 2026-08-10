import pytest

from codenerva.application.parsing.call_extractor_registry import (
    CallExtractorNotAvailableError,
    CallExtractorRegistry,
)
from codenerva.application.parsing.javascript_call_extractor import (
    JavaScriptCallExtractor,
)
from codenerva.application.parsing.python_call_extractor import (
    PythonCallExtractor,
)
from codenerva.domain.programming_language import ProgrammingLanguage


@pytest.mark.parametrize(
    ("language", "extractor_type"),
    [
        (
            ProgrammingLanguage.PYTHON,
            PythonCallExtractor,
        ),
        (
            ProgrammingLanguage.JAVASCRIPT,
            JavaScriptCallExtractor,
        ),
        (
            ProgrammingLanguage.TYPESCRIPT,
            JavaScriptCallExtractor,
        ),
        (
            ProgrammingLanguage.TSX,
            JavaScriptCallExtractor,
        ),
    ],
)
def test_registry_returns_supported_call_extractor(
    language: ProgrammingLanguage,
    extractor_type: type,
) -> None:
    registry = CallExtractorRegistry()

    extractor = registry.get(language)

    assert isinstance(extractor, extractor_type)


def test_registry_raises_for_unsupported_language() -> None:
    registry = CallExtractorRegistry()

    with pytest.raises(CallExtractorNotAvailableError):
        registry.get(ProgrammingLanguage.RUST)
