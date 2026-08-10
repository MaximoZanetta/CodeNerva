from pathlib import Path
from uuid import uuid4

import pytest

from codenerva.application.source.file_discovery import (
    FileDiscoveryService,
)
from codenerva.application.source.language_detector import (
    LanguageDetector,
)
from codenerva.domain.programming_language import ProgrammingLanguage


def test_discover_source_files(tmp_path: Path) -> None:
    repository_path = tmp_path / "repository"
    repository_path.mkdir()

    source_directory = repository_path / "src"
    source_directory.mkdir()

    (source_directory / "main.py").write_text(
        "print('hello')",
        encoding="utf-8",
    )
    (repository_path / "README.md").write_text(
        "# Example",
        encoding="utf-8",
    )

    service = FileDiscoveryService(
        language_detector=LanguageDetector(),
    )

    result = service.discover(
        snapshot_id=uuid4(),
        repository_path=repository_path,
    )

    assert len(result.files) == 2
    assert str(result.files[0].relative_path) == "README.md"
    assert str(result.files[1].relative_path) == "src/main.py"
    assert result.files[0].language is ProgrammingLanguage.MARKDOWN
    assert result.files[1].language is ProgrammingLanguage.PYTHON


def test_discovery_ignores_known_directories(
    tmp_path: Path,
) -> None:
    repository_path = tmp_path / "repository"
    repository_path.mkdir()

    git_directory = repository_path / ".git"
    git_directory.mkdir()
    (git_directory / "config").write_text(
        "ignored",
        encoding="utf-8",
    )

    node_modules = repository_path / "node_modules"
    node_modules.mkdir()
    (node_modules / "package.js").write_text(
        "ignored",
        encoding="utf-8",
    )

    (repository_path / "main.py").write_text(
        "print('included')",
        encoding="utf-8",
    )

    service = FileDiscoveryService(
        language_detector=LanguageDetector(),
    )

    result = service.discover(
        snapshot_id=uuid4(),
        repository_path=repository_path,
    )

    assert len(result.files) == 1
    assert str(result.files[0].relative_path) == "main.py"
    assert result.ignored_count >= 2


def test_discovery_ignores_large_files(
    tmp_path: Path,
) -> None:
    repository_path = tmp_path / "repository"
    repository_path.mkdir()

    (repository_path / "small.py").write_text(
        "small",
        encoding="utf-8",
    )
    (repository_path / "large.py").write_text(
        "x" * 20,
        encoding="utf-8",
    )

    service = FileDiscoveryService(
        language_detector=LanguageDetector(),
        max_file_size_bytes=10,
    )

    result = service.discover(
        snapshot_id=uuid4(),
        repository_path=repository_path,
    )

    assert len(result.files) == 1
    assert str(result.files[0].relative_path) == "small.py"
    assert result.ignored_count == 1


def test_discovery_requires_existing_directory(
    tmp_path: Path,
) -> None:
    service = FileDiscoveryService(
        language_detector=LanguageDetector(),
    )

    with pytest.raises(
        ValueError,
        match="existing directory",
    ):
        service.discover(
            snapshot_id=uuid4(),
            repository_path=tmp_path / "missing",
        )
