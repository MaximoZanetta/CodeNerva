from uuid import uuid4

from codenerva.application.qa.answer_repository_question import (
    AnswerRepositoryQuestionUseCase,
)
from codenerva.application.retrieval.context_formatter import (
    ContextFormatter,
)
from codenerva.application.retrieval.hybrid_reranker import HybridReranker
from codenerva.application.retrieval.hybrid_retrieval import (
    HybridRetrievalResult,
    HybridSemanticHit,
)
from codenerva.application.retrieval.retrieval_context_builder import (
    RetrievalContextBuilder,
)
from codenerva.domain.chunk import Chunk
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.infrastructure.fake_llm_provider import (
    FakeLLMProvider,
)
from codenerva.infrastructure.in_memory_chunk_store import (
    InMemoryChunkStore,
)


class FakeHybridRetrievalUseCase:
    def __init__(
        self,
        *,
        result: HybridRetrievalResult,
    ) -> None:
        self._result = result

    def execute(
        self,
        *,
        query: str,
        top_k: int = 3,
    ) -> HybridRetrievalResult:
        return self._result


def test_answer_repository_question_uses_retrieved_context() -> None:
    source_file_id = uuid4()

    symbol = Symbol.create(
        source_file_id=source_file_id,
        name="validationCheck",
        qualified_name="validationCheck",
        kind=SymbolKind.FUNCTION,
        start_line=1,
        end_line=3,
    )

    chunk = Chunk.create(
        snapshot_id=uuid4(),
        source_file_id=source_file_id,
        symbol_id=symbol.id,
        text=(
            "Language: javascript\n"
            "File: App.js\n"
            "Symbol: validationCheck\n"
            "Kind: FUNCTION\n\n"
            "Code:\n"
            "function validationCheck(value) {\n"
            "  return !value;\n"
            "}"
        ),
        code=("function validationCheck(value) {\n  return !value;\n}"),
        relative_path="App.js",
        language="javascript",
        qualified_name="validationCheck",
        symbol_kind="FUNCTION",
        start_line=1,
        end_line=3,
    )

    chunk_store = InMemoryChunkStore()
    chunk_store.save_many((chunk,))

    retrieval_result = HybridRetrievalResult(
        semantic_hits=(
            HybridSemanticHit(
                symbol=symbol,
                score=0.9,
            ),
        ),
        expanded_symbols=(),
    )

    hybrid_retrieval = FakeHybridRetrievalUseCase(
        result=retrieval_result,
    )

    llm_provider = FakeLLMProvider(answer="The input is validated in validationCheck.")

    use_case = AnswerRepositoryQuestionUseCase(
        hybrid_retrieval=hybrid_retrieval,
        hybrid_reranker=HybridReranker(),
        context_builder=RetrievalContextBuilder(
            chunk_store=chunk_store,
        ),
        context_formatter=ContextFormatter(),
        llm_provider=llm_provider,
    )

    result = use_case.execute(
        question="Where is user input validated?",
        top_k=3,
        max_items=6,
        max_chars=12000,
    )

    assert result.answer == "The input is validated in validationCheck."

    assert result.context_items == 1

    assert llm_provider.last_question == ("Where is user input validated?")

    assert llm_provider.last_context is not None

    assert "validationCheck" in llm_provider.last_context
    assert "function validationCheck" in llm_provider.last_context


import pytest


def test_answer_repository_question_rejects_empty_question() -> None:
    use_case = AnswerRepositoryQuestionUseCase(
        hybrid_retrieval=FakeHybridRetrievalUseCase(
            result=HybridRetrievalResult(
                semantic_hits=(),
                expanded_symbols=(),
            )
        ),
        hybrid_reranker=HybridReranker(),
        context_builder=RetrievalContextBuilder(
            chunk_store=InMemoryChunkStore(),
        ),
        context_formatter=ContextFormatter(),
        llm_provider=FakeLLMProvider(),
    )

    with pytest.raises(ValueError):
        use_case.execute(
            question="   ",
        )
