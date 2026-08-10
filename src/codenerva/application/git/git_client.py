from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass(frozen=True, slots=True)
class GitRepositoryInfo:
    commit_sha: str
    branch: str | None
    remote_url: str


class GitClient(Protocol):
    def clone(
        self,
        *,
        remote_url: str,
        destination: Path,
    ) -> None: ...

    def inspect(
        self,
        *,
        repository_path: Path,
    ) -> GitRepositoryInfo: ...
