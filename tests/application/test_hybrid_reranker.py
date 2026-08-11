from uuid import uuid4

from codenerva.application.retrieval.hybrid_reranker import (
    HybridReranker,
)
from codenerva.application.retrieval.hybrid_retrieval import (
    HybridExpandedSymbol,
    HybridRetrievalResult,
    HybridSemanticHit,
)
from codenerva.domain.symbol import Symbol, SymbolKind


def test_reranker_combines_semantic_and_graph_relevance() -> None:
    source_file_id = uuid4()

    validation = Symbol.create(
        source_file_id=source_file_id,
        name="validationCheck",
        qualified_name="validationCheck",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    handle_click = Symbol.create(
        source_file_id=source_file_id,
        name="handleClick",
        qualified_name="handleClick",
        kind=SymbolKind.FUNCTION,
        start_line=5,
        end_line=10,
    )

    streaming = Symbol.create(
        source_file_id=source_file_id,
        name="handleStreamingChat",
        qualified_name="handleStreamingChat",
        kind=SymbolKind.FUNCTION,
        start_line=12,
        end_line=20,
    )

    retrieval_result = HybridRetrievalResult(
        semantic_hits=(
            HybridSemanticHit(
                symbol=validation,
                score=0.50,
            ),
            HybridSemanticHit(
                symbol=handle_click,
                score=0.40,
            ),
        ),
        expanded_symbols=(
            HybridExpandedSymbol(
                symbol=handle_click,
                relation="CALLED_BY",
                source_symbol_id=str(validation.id),
                source_symbol_name=validation.qualified_name,
            ),
            HybridExpandedSymbol(
                symbol=streaming,
                relation="CALLS",
                source_symbol_id=str(handle_click.id),
                source_symbol_name=handle_click.qualified_name,
            ),
        ),
    )

    result = HybridReranker().rerank(
        retrieval_result=retrieval_result,
    )

    assert len(result.items) == 3

    validation_item = next(
        item for item in result.items if item.symbol.id == validation.id
    )

    handle_click_item = next(
        item for item in result.items if item.symbol.id == handle_click.id
    )

    streaming_item = next(
        item for item in result.items if item.symbol.id == streaming.id
    )

    assert validation_item.semantic_score == 0.50

    assert handle_click_item.semantic_score == 0.40
    assert handle_click_item.final_score > 0.40

    assert handle_click_item.graph_relations == ("CALLS:validationCheck",)

    assert streaming_item.semantic_score is None

    assert streaming_item.graph_relations == ("CALLED_BY:handleClick",)

    assert streaming_item.final_score > 0


def test_reranker_orders_by_final_score() -> None:
    source_file_id = uuid4()

    first = Symbol.create(
        source_file_id=source_file_id,
        name="first",
        qualified_name="first",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=2,
    )

    second = Symbol.create(
        source_file_id=source_file_id,
        name="second",
        qualified_name="second",
        kind=SymbolKind.FUNCTION,
        start_line=4,
        end_line=5,
    )

    retrieval_result = HybridRetrievalResult(
        semantic_hits=(
            HybridSemanticHit(
                symbol=first,
                score=0.30,
            ),
            HybridSemanticHit(
                symbol=second,
                score=0.60,
            ),
        ),
        expanded_symbols=(),
    )

    result = HybridReranker().rerank(
        retrieval_result=retrieval_result,
    )

    assert result.items[0].symbol.id == second.id
    assert result.items[1].symbol.id == first.id
