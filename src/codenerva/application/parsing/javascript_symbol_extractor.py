from dataclasses import dataclass

from tree_sitter import Node, Tree


@dataclass(frozen=True, slots=True)
class ExtractedSymbol:
    name: str
    kind: str
    start_line: int
    end_line: int
    parent_name: str | None


class JavaScriptSymbolExtractor:
    def extract(
        self,
        *,
        tree: Tree,
        source: bytes,
    ) -> tuple[ExtractedSymbol, ...]:
        symbols: list[ExtractedSymbol] = []

        self._visit(
            node=tree.root_node,
            source=source,
            symbols=symbols,
            enclosing_class=None,
        )

        symbols.sort(
            key=lambda symbol: (
                symbol.start_line,
                symbol.end_line,
                symbol.name,
            )
        )

        return tuple(symbols)

    def _visit(
        self,
        *,
        node: Node,
        source: bytes,
        symbols: list[ExtractedSymbol],
        enclosing_class: str | None,
    ) -> None:
        if node.type in {
            "function_declaration",
            "class_declaration",
            "method_definition",
            "variable_declarator",
        }:
            current_class = enclosing_class

        if node.type == "class_declaration":
            class_name = self._extract_name(
                node=node,
                source=source,
            )

            if class_name is not None:
                symbols.append(
                    ExtractedSymbol(
                        name=class_name,
                        kind="CLASS",
                        start_line=node.start_point.row + 1,
                        end_line=node.end_point.row + 1,
                        parent_name=None,
                    )
                )

                current_class = class_name

        elif node.type == "method_definition":
            name = self._extract_name(
                node=node,
                source=source,
            )

            if name is not None:
                symbols.append(
                    ExtractedSymbol(
                        name=name,
                        kind="METHOD",
                        start_line=node.start_point.row + 1,
                        end_line=node.end_point.row + 1,
                        parent_name=current_class,
                    )
                )

        elif node.type == "function_declaration":
            name = self._extract_name(
                node=node,
                source=source,
            )

            if name is not None:
                symbols.append(
                    ExtractedSymbol(
                        name=name,
                        kind="FUNCTION",
                        start_line=node.start_point.row + 1,
                        end_line=node.end_point.row + 1,
                        parent_name=None,
                    )
                )

        elif node.type == "variable_declarator":
            self._extract_arrow_function(
                node=node,
                source=source,
                symbols=symbols,
            )

        for child in node.named_children:
            self._visit(
                node=child,
                source=source,
                symbols=symbols,
                enclosing_class=current_class,
            )

    def _extract_arrow_function(
        self,
        *,
        node: Node,
        source: bytes,
        symbols: list[ExtractedSymbol],
    ) -> None:
        name_node = node.child_by_field_name("name")
        value_node = node.child_by_field_name("value")

        if name_node is None or value_node is None:
            return

        if value_node.type != "arrow_function":
            return

        name = self._node_text(
            node=name_node,
            source=source,
        )
        symbols.append(
            ExtractedSymbol(
                name=name,
                kind="FUNCTION",
                start_line=node.start_point.row + 1,
                end_line=node.end_point.row + 1,
                parent_name=None,
            )
        )

    def _extract_name(
        self,
        *,
        node: Node,
        source: bytes,
    ) -> str | None:
        name_node = node.child_by_field_name("name")

        if name_node is None:
            return None

        name = self._node_text(
            node=name_node,
            source=source,
        )

        return name

    def _node_text(
        self,
        *,
        node: Node,
        source: bytes,
    ) -> str:
        return source[node.start_byte : node.end_byte].decode("utf-8")
