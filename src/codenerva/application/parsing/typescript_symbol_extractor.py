from tree_sitter import Tree

from codenerva.application.parsing.javascript_symbol_extractor import (
    ExtractedSymbol,
    JavaScriptSymbolExtractor,
)


class TypeScriptSymbolExtractor(JavaScriptSymbolExtractor):
    def extract(
        self,
        *,
        tree: Tree,
        source: bytes,
    ) -> tuple[ExtractedSymbol, ...]:
        symbols = list(
            super().extract(
                tree=tree,
                source=source,
            )
        )

        for node in tree.root_node.named_children:
            if node.type != "interface_declaration":
                continue

            name = self._extract_name(
                node=node,
                source=source,
            )

            if name is None:
                continue

            symbols.append(
                ExtractedSymbol(
                    name=name,
                    kind="INTERFACE",
                    start_line=node.start_point.row + 1,
                    end_line=node.end_point.row + 1,
                    parent_name=None,
                )
            )

        symbols.sort(
            key=lambda symbol: (
                symbol.start_line,
                symbol.end_line,
                symbol.name,
            )
        )

        return tuple(symbols)
