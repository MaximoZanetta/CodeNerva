from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.parsing.typescript_path_alias_resolver import (
    TypeScriptPathAliasResolver,
)
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile


def test_resolve_typescript_path_alias(
    tmp_path,
) -> None:
    (tmp_path / "tsconfig.json").write_text(
        """
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
""",
        encoding="utf-8",
    )

    snapshot_id = uuid4()

    route_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/api/conversation/route.ts"),
        language=ProgrammingLanguage.TYPESCRIPT,
        size_bytes=100,
        content_hash="a" * 64,
    )

    api_limit_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("lib/api-limit.ts"),
        language=ProgrammingLanguage.TYPESCRIPT,
        size_bytes=100,
        content_hash="b" * 64,
    )

    resolver = TypeScriptPathAliasResolver()

    result = resolver.resolve(
        module="@/lib/api-limit",
        repository_path=tmp_path,
        snapshot_files=(
            route_file,
            api_limit_file,
        ),
    )

    assert result is not None
    assert result.id == api_limit_file.id


def test_resolve_typescript_alias_supports_index_file(
    tmp_path,
) -> None:
    (tmp_path / "tsconfig.json").write_text(
        """
{
  "compilerOptions": {
    "baseUrl": ".",
    "paths": {
      "@/*": ["./*"]
    }
  }
}
""",
        encoding="utf-8",
    )

    snapshot_id = uuid4()

    index_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("lib/subscription/index.ts"),
        language=ProgrammingLanguage.TYPESCRIPT,
        size_bytes=100,
        content_hash="a" * 64,
    )

    resolver = TypeScriptPathAliasResolver()

    result = resolver.resolve(
        module="@/lib/subscription",
        repository_path=tmp_path,
        snapshot_files=(index_file,),
    )

    assert result is not None
    assert result.id == index_file.id


def test_resolve_typescript_alias_returns_none_without_config(
    tmp_path,
) -> None:
    resolver = TypeScriptPathAliasResolver()

    result = resolver.resolve(
        module="@/lib/api-limit",
        repository_path=tmp_path,
        snapshot_files=(),
    )

    assert result is None
