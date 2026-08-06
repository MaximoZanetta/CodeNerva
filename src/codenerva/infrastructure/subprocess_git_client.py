import subprocess
from pathlib import Path

from codenerva.application.git.git_client import GitClient


class GitCloneError(Exception):
    pass


class SubprocessGitClient(GitClient):
    def clone(
        self,
        *,
        remote_url: str,
        destination: Path,
    ) -> None:
        destination.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            subprocess.run(
                [
                    "git",
                    "clone",
                    "--depth",
                    "1",
                    remote_url,
                    str(destination),
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,
            )
        except subprocess.TimeoutExpired as exc:
            raise GitCloneError("Repository cloning timed out.") from exc
        except subprocess.CalledProcessError as exc:
            error_message = exc.stderr.strip() or "Unknown Git error."

            raise GitCloneError(f"Could not clone repository: {error_message}") from exc
