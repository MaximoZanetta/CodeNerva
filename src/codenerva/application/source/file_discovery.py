from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path, PurePosixPath
from typing import ClassVar
from uuid import UUID

from codenerva.application.source.language_detector import LanguageDetector
from codenerva.domain.source_file import SourceFile


@dataclass(frozen=True, slots=True)
class FileDiscoveryResult:
    files: tuple[SourceFile, ...]
    ignored_count: int


class FileDiscoveryService:
    _ignored_directories: ClassVar[frozenset[str]] = frozenset(
        {
            ".git",
            ".venv",
            "venv",
            "__pycache__",
            "node_modules",
            "dist",
            "build",
            ".idea",
            ".vscode",
        }
    )

    def __init__(
        self,
        *,
        language_detector: LanguageDetector,
        max_file_size_bytes: int = 1_000_000,
    ) -> None:
        if max_file_size_bytes <= 0:
            raise ValueError("Maximum file size must be positive.")

        self._language_detector = language_detector
        self._max_file_size_bytes = max_file_size_bytes

    def discover(
        self,
        *,
        snapshot_id: UUID,
        repository_path: Path,
    ) -> FileDiscoveryResult:
        if not repository_path.is_dir():
            raise ValueError("Repository path must be an existing directory.")

        files: list[SourceFile] = []
        ignored_count = 0

        for path in repository_path.rglob("*"):
            relative_parts = path.relative_to(repository_path).parts

            if any(part in self._ignored_directories for part in relative_parts):
                ignored_count += 1
                continue

            if not path.is_file():
                continue

            size_bytes = path.stat().st_size

            if size_bytes > self._max_file_size_bytes:
                ignored_count += 1
                continue

            relative_path = PurePosixPath(path.relative_to(repository_path).as_posix())

            files.append(
                SourceFile.create(
                    snapshot_id=snapshot_id,
                    relative_path=relative_path,
                    language=self._language_detector.detect(relative_path),
                    size_bytes=size_bytes,
                    content_hash=self._calculate_content_hash(path),
                )
            )

        files.sort(key=lambda source_file: str(source_file.relative_path))

        return FileDiscoveryResult(
            files=tuple(files),
            ignored_count=ignored_count,
        )

    def _calculate_content_hash(
        self,
        path: Path,
    ) -> str:
        digest = sha256()

        with path.open("rb") as file:
            while chunk := file.read(64 * 1024):
                digest.update(chunk)

        return digest.hexdigest()
