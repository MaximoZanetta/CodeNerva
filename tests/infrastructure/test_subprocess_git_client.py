import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from codenerva.application.git.git_client import GitRepositoryInfo
from codenerva.infrastructure.subprocess_git_client import (
    GitCloneError,
    SubprocessGitClient,
)


def test_clone_executes_git_command(tmp_path: Path) -> None:
    destination = tmp_path / "repository"
    client = SubprocessGitClient()

    with patch("subprocess.run") as mocked_run:
        client.clone(
            remote_url="https://github.com/example/shop",
            destination=destination,
        )

    mocked_run.assert_called_once_with(
        [
            "git",
            "clone",
            "--depth",
            "1",
            "https://github.com/example/shop",
            str(destination),
        ],
        check=True,
        capture_output=True,
        text=True,
        timeout=300,
    )


def test_clone_raises_domain_error_when_git_fails(
    tmp_path: Path,
) -> None:
    client = SubprocessGitClient()

    git_error = subprocess.CalledProcessError(
        returncode=128,
        cmd=["git", "clone"],
        stderr="repository not found",
    )

    with (
        patch(
            "subprocess.run",
            side_effect=git_error,
        ),
        pytest.raises(
            GitCloneError,
            match="repository not found",
        ),
    ):
        client.clone(
            remote_url="https://github.com/example/missing",
            destination=tmp_path / "repository",
        )


def test_inspect_reads_repository_metadata(
    tmp_path: Path,
) -> None:
    client = SubprocessGitClient()
    repository_path = tmp_path / "repository"

    completed_results = [
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="abc123\n",
            stderr="",
        ),
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="main\n",
            stderr="",
        ),
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="https://github.com/example/shop\n",
            stderr="",
        ),
    ]

    with patch(
        "subprocess.run",
        side_effect=completed_results,
    ):
        result = client.inspect(
            repository_path=repository_path,
        )

    assert result == GitRepositoryInfo(
        commit_sha="abc123",
        branch="main",
        remote_url="https://github.com/example/shop",
    )


def test_inspect_supports_detached_head(
    tmp_path: Path,
) -> None:
    client = SubprocessGitClient()

    completed_results = [
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="abc123\n",
            stderr="",
        ),
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="\n",
            stderr="",
        ),
        subprocess.CompletedProcess(
            args=[],
            returncode=0,
            stdout="https://github.com/example/shop\n",
            stderr="",
        ),
    ]

    with patch(
        "subprocess.run",
        side_effect=completed_results,
    ):
        result = client.inspect(
            repository_path=tmp_path / "repository",
        )

    assert result.branch is None
