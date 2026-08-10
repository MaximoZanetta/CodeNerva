from uuid import uuid4

import pytest

from codenerva.domain.snapshot import Snapshot, SnapshotStatus


def test_create_snapshot() -> None:
    snapshot = Snapshot.create(
        repository_id=uuid4(),
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/shop",
    )

    assert snapshot.commit_sha == "a" * 40
    assert snapshot.branch == "main"
    assert snapshot.remote_url == "https://github.com/example/shop"
    assert snapshot.status is SnapshotStatus.PENDING


def test_snapshot_normalizes_commit_and_branch() -> None:
    snapshot = Snapshot.create(
        repository_id=uuid4(),
        commit_sha="A" * 40,
        branch="  main  ",
        remote_url="https://github.com/example/shop",
    )

    assert snapshot.commit_sha == "a" * 40
    assert snapshot.branch == "main"


def test_blank_branch_becomes_none() -> None:
    snapshot = Snapshot.create(
        repository_id=uuid4(),
        commit_sha="a" * 40,
        branch="   ",
        remote_url="https://github.com/example/shop",
    )

    assert snapshot.branch is None


@pytest.mark.parametrize(
    "commit_sha",
    [
        "",
        "abc123",
        "g" * 40,
        "a" * 39,
        "a" * 41,
    ],
)
def test_invalid_commit_sha_is_rejected(commit_sha: str) -> None:
    with pytest.raises(ValueError):
        Snapshot.create(
            repository_id=uuid4(),
            commit_sha=commit_sha,
            branch="main",
            remote_url="https://github.com/example/shop",
        )
