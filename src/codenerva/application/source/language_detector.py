from pathlib import PurePosixPath
from typing import ClassVar

from codenerva.domain.programming_language import ProgrammingLanguage


class LanguageDetector:
    _language_by_extension: ClassVar[dict[str, ProgrammingLanguage]] = {
        ".py": ProgrammingLanguage.PYTHON,
        ".js": ProgrammingLanguage.JAVASCRIPT,
        ".jsx": ProgrammingLanguage.JAVASCRIPT,
        ".ts": ProgrammingLanguage.TYPESCRIPT,
        ".tsx": ProgrammingLanguage.TSX,
        ".java": ProgrammingLanguage.JAVA,
        ".go": ProgrammingLanguage.GO,
        ".rs": ProgrammingLanguage.RUST,
        ".cpp": ProgrammingLanguage.CPP,
        ".cc": ProgrammingLanguage.CPP,
        ".cxx": ProgrammingLanguage.CPP,
        ".c": ProgrammingLanguage.C,
        ".h": ProgrammingLanguage.C,
        ".cs": ProgrammingLanguage.CSHARP,
        ".php": ProgrammingLanguage.PHP,
        ".rb": ProgrammingLanguage.RUBY,
        ".kt": ProgrammingLanguage.KOTLIN,
        ".kts": ProgrammingLanguage.KOTLIN,
        ".swift": ProgrammingLanguage.SWIFT,
        ".scala": ProgrammingLanguage.SCALA,
        ".html": ProgrammingLanguage.HTML,
        ".htm": ProgrammingLanguage.HTML,
        ".css": ProgrammingLanguage.CSS,
        ".json": ProgrammingLanguage.JSON,
        ".yaml": ProgrammingLanguage.YAML,
        ".yml": ProgrammingLanguage.YAML,
        ".xml": ProgrammingLanguage.XML,
        ".toml": ProgrammingLanguage.TOML,
        ".md": ProgrammingLanguage.MARKDOWN,
        ".markdown": ProgrammingLanguage.MARKDOWN,
    }

    _language_by_filename: ClassVar[dict[str, ProgrammingLanguage]] = {
        "Dockerfile": ProgrammingLanguage.DOCKERFILE,
        "Containerfile": ProgrammingLanguage.DOCKERFILE,
        "README": ProgrammingLanguage.MARKDOWN,
        "LICENSE": ProgrammingLanguage.UNKNOWN,
        "Makefile": ProgrammingLanguage.UNKNOWN,
        "Jenkinsfile": ProgrammingLanguage.UNKNOWN,
    }

    def detect(
        self,
        path: PurePosixPath,
    ) -> ProgrammingLanguage:
        filename_match = self._language_by_filename.get(path.name)

        if filename_match is not None:
            return filename_match

        return self._language_by_extension.get(
            path.suffix.lower(),
            ProgrammingLanguage.UNKNOWN,
        )
