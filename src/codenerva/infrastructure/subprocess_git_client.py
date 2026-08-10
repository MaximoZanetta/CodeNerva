import subprocess
from pathlib import Path

from codenerva.application.git.git_client import GitClient, GitRepositoryInfo


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

    def inspect(
        self,
        *,
        repository_path: Path,
    ) -> GitRepositoryInfo:
        commit_sha = self._run_git_command(
            repository_path=repository_path,
            arguments=["rev-parse", "HEAD"],
        )

        branch = self._run_git_command(
            repository_path=repository_path,
            arguments=["branch", "--show-current"],
        )

        remote_url = self._run_git_command(
            repository_path=repository_path,
            arguments=["remote", "get-url", "origin"],
        )

        return GitRepositoryInfo(
            commit_sha=commit_sha,
            branch=branch or None,
            remote_url=remote_url,
        )

    def _run_git_command(
        self,
        *,
        repository_path: Path,
        arguments: list[str],
    ) -> str:
        try:
            result = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository_path),
                    *arguments,
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except subprocess.TimeoutExpired as exc:
            raise GitCloneError("Git command timed out.") from exc
        except subprocess.CalledProcessError as exc:
            error_message = exc.stderr.strip() or "Unknown Git error."

            raise GitCloneError(f"Git command failed: {error_message}") from exc

        return result.stdout.strip()
