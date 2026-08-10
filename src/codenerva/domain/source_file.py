from dataclasses import dataclass
from pathlib import PurePosixPath
from uuid import UUID, uuid5

from codenerva.domain.programming_language import ProgrammingLanguage

SOURCE_FILE_NAMESPACE = UUID("3c52e96d-65cf-4bb8-92c0-d16f90b8f91f")


@dataclass(frozen=True, slots=True)
class SourceFile:
    id: UUID
    snapshot_id: UUID
    relative_path: PurePosixPath
    language: ProgrammingLanguage
    size_bytes: int
    content_hash: str

    @classmethod
    def create(
        cls,
        *,
        snapshot_id: UUID,
        relative_path: PurePosixPath,
        language: ProgrammingLanguage,
        size_bytes: int,
        content_hash: str,
    ) -> "SourceFile":
        if size_bytes < 0:
            raise ValueError("File size cannot be negative.")

        normalized_hash = content_hash.strip().lower()

        if len(normalized_hash) != 64:
            raise ValueError("Content hash must be a SHA-256 hexadecimal digest.")

        if not all(character in "0123456789abcdef" for character in normalized_hash):
            raise ValueError("Content hash must be a SHA-256 hexadecimal digest.")

        normalized_path = PurePosixPath(relative_path.as_posix())

        source_file_id = uuid5(
            SOURCE_FILE_NAMESPACE,
            f"{snapshot_id}:{normalized_path.as_posix()}",
        )

        return cls(
            id=source_file_id,
            snapshot_id=snapshot_id,
            relative_path=normalized_path,
            language=language,
            size_bytes=size_bytes,
            content_hash=normalized_hash,
        )
