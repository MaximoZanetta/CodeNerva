from uuid import uuid4

from codenerva.application.retrieval.hybrid_reranker import (
    HybridReranker,
)
from codenerva.application.retrieval.hybrid_retrieval import (
    HybridExpandedSymbol,
    HybridRetrievalResult,
    HybridSemanticHit,
)
from codenerva.application.retrieval.retrieval_context_builder import (
    RetrievalContextBuilder,
)
from codenerva.domain.chunk import Chunk
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.infrastructure.in_memory_chunk_store import (
    InMemoryChunkStore,
)


def test_context_builder_deduplicates_symbols() -> None:
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

    chunk_store = InMemoryChunkStore()

    validation_chunk = Chunk.create(
        snapshot_id=uuid4(),
        source_file_id=source_file_id,
        symbol_id=validation.id,
        text="function validationCheck() {}",
        relative_path="App.js",
        language="javascript",
        qualified_name="validationCheck",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=3,
        code="def login(): pass",
    )

    handle_click_chunk = Chunk.create(
        snapshot_id=validation_chunk.snapshot_id,
        source_file_id=source_file_id,
        symbol_id=handle_click.id,
        text="function handleClick() {}",
        relative_path="App.js",
        language="javascript",
        qualified_name="handleClick",
        symbol_kind="FUNCTION",
        start_line=5,
        end_line=10,
        code="def login(): pass",
    )

    chunk_store.save_many(
        (
            validation_chunk,
            handle_click_chunk,
        )
    )

    retrieval_result = HybridRetrievalResult(
        semantic_hits=(
            HybridSemanticHit(
                symbol=validation,
                score=0.8,
            ),
            HybridSemanticHit(
                symbol=handle_click,
                score=0.7,
            ),
        ),
        expanded_symbols=(
            HybridExpandedSymbol(
                symbol=handle_click,
                relation="CALLED_BY",
                source_symbol_id=str(validation.id),
                source_symbol_name=validation.qualified_name,
            ),
        ),
    )
    rerank_result = HybridReranker().rerank(
        retrieval_result=retrieval_result,
    )

    builder = RetrievalContextBuilder(
        chunk_store=chunk_store,
    )

    result = builder.build(
        rerank_result=rerank_result,
    )

    assert len(result.items) == 2

    handle_click_item = next(
        item for item in result.items if item.symbol_id == handle_click.id
    )

    assert handle_click_item.semantic_rank == 2
    assert handle_click_item.semantic_score == 0.7
    assert handle_click_item.graph_relations == ("CALLS:validationCheck",)


def test_context_builder_respects_character_budget() -> None:
    source_file_id = uuid4()
    snapshot_id = uuid4()

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

    chunk_store = InMemoryChunkStore()

    first_chunk = Chunk.create(
        snapshot_id=snapshot_id,
        source_file_id=source_file_id,
        symbol_id=first.id,
        text="first",
        code="a" * 100,
        relative_path="test.py",
        language="python",
        qualified_name="first",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=2,
    )

    second_chunk = Chunk.create(
        snapshot_id=snapshot_id,
        source_file_id=source_file_id,
        symbol_id=second.id,
        text="second",
        code="b" * 100,
        relative_path="test.py",
        language="python",
        qualified_name="second",
        symbol_kind="FUNCTION",
        start_line=4,
        end_line=5,
    )

    chunk_store.save_many(
        (
            first_chunk,
            second_chunk,
        )
    )

    retrieval_result = HybridRetrievalResult(
        semantic_hits=(
            HybridSemanticHit(
                symbol=first,
                score=0.9,
            ),
            HybridSemanticHit(
                symbol=second,
                score=0.8,
            ),
        ),
        expanded_symbols=(),
    )
    rerank_result = HybridReranker().rerank(
        retrieval_result=retrieval_result,
    )

    builder = RetrievalContextBuilder(
        chunk_store=chunk_store,
    )

    result = builder.build(
        rerank_result=rerank_result,
        max_items=6,
        max_chars=150,
    )

    assert len(result.items) == 1
    assert result.items[0].symbol_id == first.id
