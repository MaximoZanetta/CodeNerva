import ast

from tree_sitter import Tree

from codenerva.application.parsing.extracted_call import ExtractedCall


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
                (
                    ast.FunctionDef,
                    ast.AsyncFunctionDef,
                ),
            ):
                continue

            caller_name = node.name

            for child in ast.walk(node):
                if not isinstance(
                    child,
                    ast.Call,
                ):
                    continue

                extracted = self._extract_callee(child.func)

                if extracted is None:
                    continue

                callee_name, owner_name = extracted

                calls.append(
                    ExtractedCall(
                        caller_name=caller_name,
                        callee_name=callee_name,
                        owner_name=owner_name,
                        line=child.lineno,
                    )
                )

        return tuple(calls)

    def _extract_callee(
        self,
        node: ast.expr,
    ) -> tuple[str, str | None] | None:
        if isinstance(node, ast.Name):
            return (
                node.id,
                None,
            )

        if isinstance(node, ast.Attribute):
            owner_name = self._extract_owner_name(node.value)

            return (
                node.attr,
                owner_name,
            )

        return None

    def _extract_owner_name(
        self,
        node: ast.expr,
    ) -> str | None:
        if isinstance(node, ast.Name):
            return node.id

        if isinstance(node, ast.Attribute):
            parts: list[str] = []

            current: ast.expr = node

            while isinstance(
                current,
                ast.Attribute,
            ):
                parts.append(current.attr)

                current = current.value

            if isinstance(
                current,
                ast.Name,
            ):
                parts.append(current.id)

                return ".".join(reversed(parts))

        return None
