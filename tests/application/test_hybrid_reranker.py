from pathlib import PurePosixPath
from uuid import uuid4

from codenerva.application.retrieval.hybrid_reranker import (
    HybridReranker,
)
from codenerva.application.retrieval.hybrid_retrieval import (
    HybridExpandedSymbol,
    HybridRetrievalResult,
    HybridSemanticHit,
)
from codenerva.domain.programming_language import (
    ProgrammingLanguage,
)
from codenerva.domain.source_file import SourceFile
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.infrastructure.in_memory_source_file_store import (
    InMemorySourceFileStore,
)


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


def test_reranker_penalizes_tests_for_non_testing_question() -> None:
    snapshot_id = uuid4()

    production_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/fizz/controller.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    test_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/fizz/model_test.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="b" * 64,
    )

    source_file_store = InMemorySourceFileStore()

    source_file_store.save_many(
        (
            production_file,
            test_file,
        )
    )

    production_symbol = Symbol.create(
        source_file_id=production_file.id,
        name="post_fizz",
        qualified_name="post_fizz",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    test_symbol = Symbol.create(
        source_file_id=test_file.id,
        name="fizz",
        qualified_name="fizz",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    retrieval_result = HybridRetrievalResult(
        semantic_hits=(
            HybridSemanticHit(
                symbol=test_symbol,
                score=0.60,
            ),
            HybridSemanticHit(
                symbol=production_symbol,
                score=0.57,
            ),
        ),
        expanded_symbols=(),
    )

    result = HybridReranker(
        source_file_store=source_file_store,
    ).rerank(
        retrieval_result=retrieval_result,
        question=("How does the fizz feature work?"),
    )

    assert result.items[0].symbol.id == production_symbol.id

    assert result.items[1].symbol.id == test_symbol.id


def test_reranker_does_not_penalize_tests_for_testing_question() -> None:
    snapshot_id = uuid4()

    production_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/fizz/controller.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="a" * 64,
    )

    test_file = SourceFile.create(
        snapshot_id=snapshot_id,
        relative_path=PurePosixPath("app/fizz/model_test.py"),
        language=ProgrammingLanguage.PYTHON,
        size_bytes=100,
        content_hash="b" * 64,
    )

    source_file_store = InMemorySourceFileStore()

    source_file_store.save_many(
        (
            production_file,
            test_file,
        )
    )

    production_symbol = Symbol.create(
        source_file_id=production_file.id,
        name="post_fizz",
        qualified_name="post_fizz",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    test_symbol = Symbol.create(
        source_file_id=test_file.id,
        name="fizz",
        qualified_name="fizz",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    retrieval_result = HybridRetrievalResult(
        semantic_hits=(
            HybridSemanticHit(
                symbol=test_symbol,
                score=0.60,
            ),
            HybridSemanticHit(
                symbol=production_symbol,
                score=0.57,
            ),
        ),
        expanded_symbols=(),
    )

    result = HybridReranker(
        source_file_store=source_file_store,
    ).rerank(
        retrieval_result=retrieval_result,
        question=("How is the fizz feature tested?"),
    )

    assert result.items[0].symbol.id == test_symbol.id


def test_reranker_boosts_executable_symbols_for_behavioral_question() -> None:
    source_file_id = uuid4()

    service_class = Symbol.create(
        source_file_id=source_file_id,
        name="FizzService",
        qualified_name="FizzService",
        kind=SymbolKind.CLASS,
        start_line=1,
        end_line=20,
    )

    create_method = Symbol.create(
        source_file_id=source_file_id,
        name="create",
        qualified_name="FizzService.create",
        kind=SymbolKind.METHOD,
        start_line=10,
        end_line=15,
        parent_symbol_id=service_class.id,
    )

    retrieval_result = HybridRetrievalResult(
        semantic_hits=(
            HybridSemanticHit(
                symbol=service_class,
                score=0.50,
            ),
            HybridSemanticHit(
                symbol=create_method,
                score=0.49,
            ),
        ),
        expanded_symbols=(),
    )

    result = HybridReranker().rerank(
        retrieval_result=retrieval_result,
        question="How does Fizz creation work?",
    )

    assert result.items[0].symbol.id == create_method.id

    assert result.items[0].final_score == 0.54

    assert result.items[1].final_score == 0.50


def test_reranker_does_not_boost_executable_symbols_for_non_behavioral_question() -> (
    None
):
    source_file_id = uuid4()

    service_class = Symbol.create(
        source_file_id=source_file_id,
        name="FizzService",
        qualified_name="FizzService",
        kind=SymbolKind.CLASS,
        start_line=1,
        end_line=20,
    )

    create_method = Symbol.create(
        source_file_id=source_file_id,
        name="create",
        qualified_name="FizzService.create",
        kind=SymbolKind.METHOD,
        start_line=10,
        end_line=15,
        parent_symbol_id=service_class.id,
    )

    retrieval_result = HybridRetrievalResult(
        semantic_hits=(
            HybridSemanticHit(
                symbol=service_class,
                score=0.50,
            ),
            HybridSemanticHit(
                symbol=create_method,
                score=0.49,
            ),
        ),
        expanded_symbols=(),
    )

    result = HybridReranker().rerank(
        retrieval_result=retrieval_result,
        question="Where is FizzService defined?",
    )

    assert result.items[0].symbol.id == service_class.id

    assert result.items[0].final_score == 0.50

    assert result.items[1].final_score == 0.49
