from uuid import uuid4

import pytest

from codenerva.domain.repository import (
    Repository,
    RepositoryProvider,
    RepositoryStatus,
)


def test_create_github_repository() -> None:
    project_id = uuid4()

    repository = Repository.create_github(
        project_id=project_id,
        remote_url="https://github.com/example/shop",
    )

    assert repository.project_id == project_id
    assert repository.provider is RepositoryProvider.GITHUB
    assert repository.remote_url == "https://github.com/example/shop"
    assert repository.owner == "example"
    assert repository.name == "shop"
    assert repository.status is RepositoryStatus.ACTIVE


def test_repository_url_is_normalized() -> None:
    repository = Repository.create_github(
        project_id=uuid4(),
        remote_url="  https://github.com/example/shop.git/  ",
    )

    assert repository.remote_url == "https://github.com/example/shop"


@pytest.mark.parametrize(
    "url",
    [
        "",
        "https://gitlab.com/example/shop",
        "https://github.com/example",
        "https://github.com/example/shop/extra",
    ],
)
def test_invalid_repository_url_is_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        Repository.create_github(
            project_id=uuid4(),
            remote_url=url,
        )
