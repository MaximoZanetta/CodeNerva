import ast
from dataclasses import dataclass

from tree_sitter import Tree


@dataclass(frozen=True, slots=True)
class ExtractedCall:
    caller_name: str
    callee_name: str
    line: int


class PythonCallExtractor:
    def extract(
        self,
        *,
        tree: Tree,
        source: bytes,
    ) -> tuple[ExtractedCall, ...]:
        del tree

        root = ast.parse(source.decode("utf-8"))

        calls: list[ExtractedCall] = []

        for node in ast.walk(root):
            if not isinstance(
                node,
                (ast.FunctionDef, ast.AsyncFunctionDef),
            ):
                continue

            caller_name = node.name

            for child in ast.walk(node):
                if not isinstance(child, ast.Call):
                    continue

                callee_name = self._extract_callee_name(child.func)

                if callee_name is None:
                    continue

                calls.append(
                    ExtractedCall(
                        caller_name=caller_name,
                        callee_name=callee_name,
                        line=child.lineno,
                    )
                )

        return tuple(calls)

    def _extract_callee_name(
        self,
        node: ast.expr,
    ) -> str | None:
        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            return node.attr

        return None
