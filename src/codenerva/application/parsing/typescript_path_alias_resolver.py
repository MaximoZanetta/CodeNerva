import json
from pathlib import PurePosixPath

from codenerva.domain.source_file import SourceFile


class TypeScriptPathAliasResolver:
    def resolve(
        self,
        *,
        module: str,
        repository_path,
        snapshot_files: tuple[SourceFile, ...],
    ) -> SourceFile | None:
        config = self._load_config(repository_path)

        if config is None:
            return None

        compiler_options = config.get(
            "compilerOptions",
            {},
        )

        base_url = compiler_options.get(
            "baseUrl",
            ".",
        )

        paths = compiler_options.get(
            "paths",
            {},
        )

        if not isinstance(paths, dict):
            return None

        for pattern, targets in paths.items():
            wildcard_value = self._match_pattern(
                module=module,
                pattern=pattern,
            )

            if wildcard_value is None:
                continue

            if not isinstance(targets, list):
                continue

            for target_pattern in targets:
                if not isinstance(target_pattern, str):
                    continue

                resolved_target = self._apply_target_pattern(
                    target_pattern=target_pattern,
                    wildcard_value=wildcard_value,
                )

                candidate_base = PurePosixPath(base_url) / PurePosixPath(
                    resolved_target
                )

                result = self._find_snapshot_file(
                    candidate_base=candidate_base,
                    snapshot_files=snapshot_files,
                )

                if result is not None:
                    return result

        return None

    def _load_config(
        self,
        repository_path,
    ) -> dict | None:
        for filename in (
            "tsconfig.json",
            "jsconfig.json",
        ):
            path = repository_path / filename

            if not path.exists():
                continue

            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                return None

        return None

    def _match_pattern(
        self,
        *,
        module: str,
        pattern: str,
    ) -> str | None:
        if "*" not in pattern:
            if module == pattern:
                return ""

            return None

        prefix, suffix = pattern.split(
            "*",
            maxsplit=1,
        )

        if not module.startswith(prefix):
            return None

        if suffix and not module.endswith(suffix):
            return None

        end_index = len(module) - len(suffix) if suffix else len(module)

        return module[len(prefix) : end_index]

    def _apply_target_pattern(
        self,
        *,
        target_pattern: str,
        wildcard_value: str,
    ) -> str:
        if "*" not in target_pattern:
            return target_pattern

        return target_pattern.replace(
            "*",
            wildcard_value,
        )

    def _find_snapshot_file(
        self,
        *,
        candidate_base: PurePosixPath,
        snapshot_files: tuple[SourceFile, ...],
    ) -> SourceFile | None:
        candidate_paths = self._candidate_paths(candidate_base)

        for source_file in snapshot_files:
            if source_file.relative_path in candidate_paths:
                return source_file

        return None

    def _candidate_paths(
        self,
        base: PurePosixPath,
    ) -> tuple[PurePosixPath, ...]:
        if base.suffix:
            return (base,)

        return (
            base.with_suffix(".ts"),
            base.with_suffix(".tsx"),
            base.with_suffix(".js"),
            base.with_suffix(".jsx"),
            base / "index.ts",
            base / "index.tsx",
            base / "index.js",
            base / "index.jsx",
        )
