from dataclasses import dataclass

from tree_sitter import Node, Tree


@dataclass(frozen=True, slots=True)
class ExtractedImport:
    module: str
    imported_name: str | None
    alias: str | None
    line: int


class JavaScriptImportExtractor:
    def extract(
        self,
        *,
        tree: Tree,
        source: bytes,
    ) -> tuple[ExtractedImport, ...]:
        imports: list[ExtractedImport] = []

        for node in tree.root_node.named_children:
            if node.type != "import_statement":
                continue

            source_node = node.child_by_field_name("source")

            if source_node is None:
                continue

            module = self._node_text(
                node=source_node,
                source=source,
            ).strip("\"'")

            clause = next(
                (
                    child
                    for child in node.named_children
                    if child.type == "import_clause"
                ),
                None,
            )

            if clause is None:
                imports.append(
                    ExtractedImport(
                        module=module,
                        imported_name=None,
                        alias=None,
                        line=node.start_point.row + 1,
                    )
                )
                continue

            self._extract_import_clause(
                node=clause,
                module=module,
                source=source,
                line=node.start_point.row + 1,
                imports=imports,
            )

        return tuple(imports)

    def _extract_import_clause(
        self,
        *,
        node: Node,
        module: str,
        source: bytes,
        line: int,
        imports: list[ExtractedImport],
    ) -> None:
        for child in node.named_children:
            if child.type == "identifier":
                imports.append(
                    ExtractedImport(
                        module=module,
                        imported_name="default",
                        alias=self._node_text(
                            node=child,
                            source=source,
                        ),
                        line=line,
                    )
                )

            elif child.type == "namespace_import":
                alias_node = child.child_by_field_name("name")

                imports.append(
                    ExtractedImport(
                        module=module,
                        imported_name="*",
                        alias=(
                            self._node_text(
                                node=alias_node,
                                source=source,
                            )
                            if alias_node is not None
                            else None
                        ),
                        line=line,
                    )
                )

            elif child.type == "named_imports":
                for specifier in child.named_children:
                    if specifier.type != "import_specifier":
                        continue

                    name_node = specifier.child_by_field_name("name")
                    alias_node = specifier.child_by_field_name("alias")

                    if name_node is None:
                        continue

                    imports.append(
                        ExtractedImport(
                            module=module,
                            imported_name=self._node_text(
                                node=name_node,
                                source=source,
                            ),
                            alias=(
                                self._node_text(
                                    node=alias_node,
                                    source=source,
                                )
                                if alias_node is not None
                                else None
                            ),
                            line=line,
                        )
                    )

    def _node_text(
        self,
        *,
        node: Node,
        source: bytes,
    ) -> str:
        return source[node.start_byte : node.end_byte].decode("utf-8")
