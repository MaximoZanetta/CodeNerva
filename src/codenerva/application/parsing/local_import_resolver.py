from dataclasses import dataclass
from pathlib import PurePosixPath

from codenerva.domain.import_reference import ImportReference
from codenerva.domain.programming_language import ProgrammingLanguage
from codenerva.domain.source_file import SourceFile


@dataclass(frozen=True, slots=True)
class ResolvedImport:
    import_reference_id: object
    target_source_file_id: object


class LocalImportResolver:
    def resolve(
        self,
        *,
        source_file: SourceFile,
        import_reference: ImportReference,
        snapshot_files: tuple[SourceFile, ...],
    ) -> SourceFile | None:
        module = import_reference.module

        if not module.startswith("."):
            return None

        source_directory = source_file.relative_path.parent

        if source_file.language is ProgrammingLanguage.PYTHON:
            normalized = self._resolve_python_module_path(
                source_directory=source_directory,
                module=module,
            )
        else:
            candidate_path = PurePosixPath(
                source_directory,
                module,
            )

            normalized = self._normalize(candidate_path)

        candidates = self._candidate_paths(normalized)

        file_by_path = {source.relative_path: source for source in snapshot_files}

        for candidate in candidates:
            target = file_by_path.get(candidate)

            if target is not None:
                return target

        return None

    def _candidate_paths(
        self,
        path: PurePosixPath,
    ) -> tuple[PurePosixPath, ...]:
        if path.suffix:
            return (path,)

        return (
            path,
            PurePosixPath(f"{path}.py"),
            PurePosixPath(f"{path}.js"),
            PurePosixPath(f"{path}.ts"),
            PurePosixPath(f"{path}.tsx"),
            path / "__init__.py",
            path / "index.js",
            path / "index.ts",
            path / "index.tsx",
        )

    def _normalize(
        self,
        path: PurePosixPath,
    ) -> PurePosixPath:
        parts: list[str] = []

        for part in path.parts:
            if part == ".":
                continue

            if part == "..":
                if parts:
                    parts.pop()
                continue

            parts.append(part)

        return PurePosixPath(*parts)

    def _resolve_python_module_path(
        self,
        *,
        source_directory: PurePosixPath,
        module: str,
    ) -> PurePosixPath:
        relative_level = len(module) - len(module.lstrip("."))

        base_directory = source_directory

        for _ in range(relative_level - 1):
            base_directory = base_directory.parent

        module_name = module.lstrip(".")

        if not module_name:
            return base_directory

        module_parts = module_name.split(".")

        return PurePosixPath(
            base_directory,
            *module_parts,
        )
