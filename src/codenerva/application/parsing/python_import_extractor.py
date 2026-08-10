import ast
from dataclasses import dataclass

from tree_sitter import Tree


@dataclass(frozen=True, slots=True)
class ExtractedImport:
    module: str
    imported_name: str | None
    alias: str | None
    line: int


class PythonImportExtractor:
    def extract(
        self,
        *,
        tree: Tree,
        source: bytes,
    ) -> tuple[ExtractedImport, ...]:
        del tree
        source_text = source.decode("utf-8")
        root = ast.parse(source_text)

        imports: list[ExtractedImport] = []

        for node in ast.walk(root):
            if isinstance(node, ast.Import):
                for imported in node.names:
                    imports.append(
                        ExtractedImport(
                            module=imported.name,
                            imported_name=None,
                            alias=imported.asname,
                            line=node.lineno,
                        )
                    )

            elif isinstance(node, ast.ImportFrom):
                module = self._build_relative_module(node)

                for imported in node.names:
                    imports.append(
                        ExtractedImport(
                            module=module,
                            imported_name=imported.name,
                            alias=imported.asname,
                            line=node.lineno,
                        )
                    )

        imports.sort(
            key=lambda item: (
                item.line,
                item.module,
                item.imported_name or "",
            )
        )

        return tuple(imports)

    def _build_relative_module(
        self,
        node: ast.ImportFrom,
    ) -> str:
        prefix = "." * node.level
        module = node.module or ""

        return f"{prefix}{module}"
