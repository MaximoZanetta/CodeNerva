from pathlib import PurePosixPath

import pytest

from codenerva.application.source.language_detector import (
    LanguageDetector,
)
from codenerva.domain.programming_language import (
    ProgrammingLanguage,
)


@pytest.mark.parametrize(
    ("path", "expected_language"),
    [
        ("src/main.py", ProgrammingLanguage.PYTHON),
        ("web/index.js", ProgrammingLanguage.JAVASCRIPT),
        ("web/component.tsx", ProgrammingLanguage.TSX),
        ("service/main.go", ProgrammingLanguage.GO),
        ("Cargo.toml", ProgrammingLanguage.TOML),
        ("README.md", ProgrammingLanguage.MARKDOWN),
        ("Dockerfile", ProgrammingLanguage.DOCKERFILE),
        ("Containerfile", ProgrammingLanguage.DOCKERFILE),
        ("README", ProgrammingLanguage.MARKDOWN),
    ],
)
def test_detect_language(
    path: str,
    expected_language: ProgrammingLanguage,
) -> None:
    detector = LanguageDetector()

    result = detector.detect(PurePosixPath(path))

    assert result is expected_language


def test_detection_is_case_insensitive_for_extensions() -> None:
    detector = LanguageDetector()

    result = detector.detect(PurePosixPath("README.MD"))

    assert result is ProgrammingLanguage.MARKDOWN


def test_unknown_extension_returns_unknown() -> None:
    detector = LanguageDetector()

    result = detector.detect(PurePosixPath("src/file.xyz"))

    assert result is ProgrammingLanguage.UNKNOWN


def test_unknown_special_filename_returns_unknown() -> None:
    detector = LanguageDetector()

    result = detector.detect(PurePosixPath("Makefile"))

    assert result is ProgrammingLanguage.UNKNOWN
