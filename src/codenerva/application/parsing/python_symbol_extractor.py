import ast
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ExtractedSymbol:
    name: str
    kind: str
    start_line: int
    end_line: int
    parent_name: str | None


class PythonSymbolExtractor:
    def extract(
        self,
        *,
        tree: object,
        source: bytes,
    ) -> tuple[ExtractedSymbol, ...]:
        del tree

        source_text = source.decode("utf-8")

        root = ast.parse(source_text)

        symbols: list[ExtractedSymbol] = []

        self._visit_body(
            body=root.body,
            symbols=symbols,
            enclosing_class=None,
            inside_function=False,
        )

        return tuple(symbols)

    def _visit_body(
        self,
        *,
        body: list[ast.stmt],
        symbols: list[ExtractedSymbol],
        enclosing_class: str | None,
        inside_function: bool,
    ) -> None:
        for node in body:
            if isinstance(node, ast.ClassDef):
                symbols.append(
                    ExtractedSymbol(
                        name=node.name,
                        kind="CLASS",
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        parent_name=enclosing_class,
                    )
                )

                self._visit_body(
                    body=node.body,
                    symbols=symbols,
                    enclosing_class=node.name,
                    inside_function=False,
                )

            elif isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                is_method = enclosing_class is not None and not inside_function

                symbols.append(
                    ExtractedSymbol(
                        name=node.name,
                        kind="METHOD" if is_method else "FUNCTION",
                        start_line=node.lineno,
                        end_line=node.end_lineno or node.lineno,
                        parent_name=(enclosing_class if is_method else None),
                    )
                )

                self._visit_body(
                    body=node.body,
                    symbols=symbols,
                    enclosing_class=enclosing_class,
                    inside_function=True,
                )
