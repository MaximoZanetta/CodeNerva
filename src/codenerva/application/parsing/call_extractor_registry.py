from codenerva.application.parsing.call_extractor import CallExtractor
from codenerva.application.parsing.javascript_call_extractor import (
    JavaScriptCallExtractor,
)
from codenerva.application.parsing.python_call_extractor import (
    PythonCallExtractor,
)
from codenerva.domain.programming_language import ProgrammingLanguage


class CallExtractorNotAvailableError(Exception):
    pass


class CallExtractorRegistry:
    def __init__(self) -> None:
        javascript_extractor = JavaScriptCallExtractor()

        self._extractors: dict[
            ProgrammingLanguage,
            CallExtractor,
        ] = {
            ProgrammingLanguage.PYTHON: PythonCallExtractor(),
            ProgrammingLanguage.JAVASCRIPT: javascript_extractor,
            ProgrammingLanguage.TYPESCRIPT: javascript_extractor,
            ProgrammingLanguage.TSX: javascript_extractor,
        }

    def get(
        self,
        language: ProgrammingLanguage,
    ) -> CallExtractor:
        extractor = self._extractors.get(language)

        if extractor is None:
            raise CallExtractorNotAvailableError(
                f"No call extractor available for {language.value}."
            )

        return extractor
