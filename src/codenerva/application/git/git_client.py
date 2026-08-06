from pathlib import Path
from typing import Protocol


class GitClient(Protocol):
    def clone(
        self,
        *,
        remote_url: str,
        destination: Path,
    ) -> None: ...
