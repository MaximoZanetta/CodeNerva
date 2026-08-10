import pytest

from codenerva.application.parsing.import_extractor_registry import (
    ImportExtractorNotAvailableError,
    ImportExtractorRegistry,
)
from codenerva.application.parsing.javascript_import_extractor import (
    JavaScriptImportExtractor,
)
from codenerva.application.parsing.python_import_extractor import (
    PythonImportExtractor,
)
from codenerva.domain.programming_language import ProgrammingLanguage


@pytest.mark.parametrize(
    ("language", "extractor_type"),
    [
        (
            ProgrammingLanguage.PYTHON,
            PythonImportExtractor,
        ),
        (
            ProgrammingLanguage.JAVASCRIPT,
            JavaScriptImportExtractor,
        ),
        (
            ProgrammingLanguage.TYPESCRIPT,
            JavaScriptImportExtractor,
        ),
        (
            ProgrammingLanguage.TSX,
            JavaScriptImportExtractor,
        ),
    ],
)
def test_registry_returns_supported_import_extractor(
    language: ProgrammingLanguage,
    extractor_type: type,
) -> None:
    registry = ImportExtractorRegistry()

    extractor = registry.get(language)

    assert isinstance(extractor, extractor_type)


def test_registry_raises_for_unsupported_language() -> None:
    registry = ImportExtractorRegistry()

    with pytest.raises(ImportExtractorNotAvailableError):
        registry.get(ProgrammingLanguage.RUST)
