from uuid import uuid4

from codenerva.application.retrieval.context_formatter import (
    ContextFormatter,
)
from codenerva.application.retrieval.retrieval_context_builder import (
    RetrievalContext,
    RetrievalContextItem,
    RetrievalOrigin,
)
from codenerva.domain.chunk import Chunk


def test_context_formatter_formats_code_context() -> None:
    symbol_id = uuid4()

    chunk = Chunk.create(
        snapshot_id=uuid4(),
        source_file_id=uuid4(),
        symbol_id=symbol_id,
        text="function validationCheck(value) {\n  return !value;\n}",
        relative_path="client-react/src/App.js",
        language="javascript",
        qualified_name="validationCheck",
        symbol_kind="FUNCTION",
        start_line=10,
        end_line=12,
        code="function validationCheck(value) {\n  return !value;\n}",
    )

    context = RetrievalContext(
        items=(
            RetrievalContextItem(
                symbol_id=symbol_id,
                qualified_name="validationCheck",
                chunk=chunk,
                semantic_score=0.4558,
                semantic_rank=1,
                graph_relations=("CALLED_BY:handleClick",),
                retrieval_origin=RetrievalOrigin.BOTH,
                final_score=0.70,
            ),
        )
    )

    formatter = ContextFormatter()

    result = formatter.format(
        context=context,
    )

    assert "=== CODE CONTEXT ===" in result
    assert "[1] validationCheck" in result
    assert "File: client-react/src/App.js" in result
    assert "Language: javascript" in result
    assert "Kind: FUNCTION" in result
    assert "Semantic rank: 1" in result
    assert "Semantic score: 0.4558" in result
    assert "CALLED_BY:handleClick" in result
    assert "function validationCheck" in result


def test_context_formatter_handles_empty_context() -> None:
    formatter = ContextFormatter()

    result = formatter.format(
        context=RetrievalContext(
            items=(),
        )
    )

    assert result == "No relevant code context was found."
