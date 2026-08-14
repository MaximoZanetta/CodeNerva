from tree_sitter import Node, Tree

from codenerva.application.parsing.extracted_call import ExtractedCall


class JavaScriptCallExtractor:
    def extract(
        self,
        *,
        tree: Tree,
        source: bytes,
    ) -> tuple[ExtractedCall, ...]:
        calls: list[ExtractedCall] = []

        self._visit(
            node=tree.root_node,
            source=source,
            calls=calls,
            current_caller=None,
        )

        return tuple(calls)

    def _visit(
        self,
        *,
        node: Node,
        source: bytes,
        calls: list[ExtractedCall],
        current_caller: str | None,
    ) -> None:
        caller = current_caller

        if node.type == "function_declaration":
            caller = self._extract_name(
                node=node,
                source=source,
            )

        elif node.type == "variable_declarator":
            name_node = node.child_by_field_name("name")
            value_node = node.child_by_field_name("value")

            if (
                name_node is not None
                and value_node is not None
                and value_node.type == "arrow_function"
            ):
                caller = self._node_text(
                    node=name_node,
                    source=source,
                )

        elif node.type == "call_expression" and caller is not None:
            function_node = node.child_by_field_name("function")

            if function_node is not None:
                callee_name = self._extract_call_name(
                    node=function_node,
                    source=source,
                )

                if callee_name is not None:
                    calls.append(
                        ExtractedCall(
                            caller_name=caller,
                            callee_name=callee_name,
                            line=node.start_point.row + 1,
                        )
                    )

        for child in node.named_children:
            self._visit(
                node=child,
                source=source,
                calls=calls,
                current_caller=caller,
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

        return self._node_text(
            node=name_node,
            source=source,
        )

    def _extract_call_name(
        self,
        *,
        node: Node,
        source: bytes,
    ) -> str | None:
        if node.type == "identifier":
            return self._node_text(
                node=node,
                source=source,
            )

        if node.type == "member_expression":
            property_node = node.child_by_field_name("property")

            if property_node is None:
                return None

            return self._node_text(
                node=property_node,
                source=source,
            )

        return None

    def _node_text(
        self,
        *,
        node: Node,
        source: bytes,
    ) -> str:
        return source[node.start_byte : node.end_byte].decode("utf-8")
