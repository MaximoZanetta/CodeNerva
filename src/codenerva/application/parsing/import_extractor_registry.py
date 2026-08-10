from codenerva.application.parsing.import_extractor import ImportExtractor
from codenerva.application.parsing.javascript_import_extractor import (
    JavaScriptImportExtractor,
)
from codenerva.application.parsing.python_import_extractor import (
    PythonImportExtractor,
)
from codenerva.domain.programming_language import ProgrammingLanguage


class ImportExtractorNotAvailableError(Exception):
    pass


class ImportExtractorRegistry:
    def __init__(self) -> None:
        javascript_extractor = JavaScriptImportExtractor()

        self._extractors: dict[
            ProgrammingLanguage,
            ImportExtractor,
        ] = {
            ProgrammingLanguage.PYTHON: PythonImportExtractor(),
            ProgrammingLanguage.JAVASCRIPT: javascript_extractor,
            ProgrammingLanguage.TYPESCRIPT: javascript_extractor,
            ProgrammingLanguage.TSX: javascript_extractor,
        }

    def get(
        self,
        language: ProgrammingLanguage,
    ) -> ImportExtractor:
        extractor = self._extractors.get(language)

        if extractor is None:
            raise ImportExtractorNotAvailableError(
                f"No import extractor available for {language.value}."
            )

        return extractor
