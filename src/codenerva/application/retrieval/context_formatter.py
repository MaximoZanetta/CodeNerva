from codenerva.application.retrieval.retrieval_context_builder import (
    RetrievalContext,
    RetrievalContextItem,
)


class ContextFormatter:
    def format(
        self,
        *,
        context: RetrievalContext,
    ) -> str:
        if not context.items:
            return "No relevant code context was found."

        sections = [
            "=== CODE CONTEXT ===",
        ]

        for index, item in enumerate(
            context.items,
            start=1,
        ):
            sections.append(
                self._format_item(
                    index=index,
                    item=item,
                )
            )

        return "\n\n".join(sections)

    def _format_item(
        self,
        *,
        index: int,
        item: RetrievalContextItem,
    ) -> str:
        lines = [
            f"[{index}] {item.qualified_name}",
            f"File: {item.chunk.relative_path}",
            f"Language: {item.chunk.language}",
            f"Kind: {item.chunk.symbol_kind}",
        ]

        if item.semantic_rank is not None:
            lines.append(f"Semantic rank: {item.semantic_rank}")

        if item.semantic_score is not None:
            lines.append(f"Semantic score: {item.semantic_score:.4f}")

        if item.graph_relations:
            lines.append("Graph relations: " + ", ".join(item.graph_relations))

        lines.extend(
            (
                "",
                "Code:",
                item.chunk.code,
            )
        )

        return "\n".join(lines)
