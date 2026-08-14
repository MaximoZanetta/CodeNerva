from uuid import UUID, uuid4

import pytest

from codenerva.application.qa.answer_repository_question import (
    AnswerRepositoryQuestionUseCase,
    SnapshotNotFoundError,
)
from codenerva.application.retrieval.context_formatter import (
    ContextFormatter,
)
from codenerva.application.retrieval.hybrid_reranker import (
    HybridReranker,
)
from codenerva.application.retrieval.hybrid_retrieval import (
    HybridRetrievalResult,
    HybridSemanticHit,
)
from codenerva.application.retrieval.retrieval_context_builder import (
    RetrievalContextBuilder,
    RetrievalOrigin,
)
from codenerva.domain.chunk import Chunk
from codenerva.domain.snapshot import Snapshot
from codenerva.domain.symbol import Symbol, SymbolKind
from codenerva.infrastructure.fake_llm_provider import (
    FakeLLMProvider,
)
from codenerva.infrastructure.in_memory_chunk_store import (
    InMemoryChunkStore,
)
from codenerva.infrastructure.in_memory_snapshot_store import (
    InMemorySnapshotStore,
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
        snapshot_id: UUID,
        top_k: int = 3,
    ) -> HybridRetrievalResult:
        return self._result


def test_answer_repository_question_uses_retrieved_context() -> None:
    snapshot = Snapshot.create(
        repository_id=uuid4(),
        commit_sha="a" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    ).mark_ready()

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)

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
        snapshot_id=snapshot.id,
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

    llm_provider = FakeLLMProvider(
        answer=("The input is validated in validationCheck.")
    )

    use_case = AnswerRepositoryQuestionUseCase(
        hybrid_retrieval=hybrid_retrieval,
        hybrid_reranker=HybridReranker(),
        context_builder=RetrievalContextBuilder(
            chunk_store=chunk_store,
        ),
        context_formatter=ContextFormatter(),
        llm_provider=llm_provider,
        snapshot_store=snapshot_store,
    )

    result = use_case.execute(
        snapshot_id=snapshot.id,
        question="Where is user input validated?",
        top_k=3,
        max_items=6,
        max_chars=12000,
    )

    assert result.answer == "The input is validated in validationCheck."

    assert result.context_items == 1

    assert len(result.sources) == 1

    source = result.sources[0]

    assert source.relative_path == "App.js"
    assert source.qualified_name == "validationCheck"
    assert source.symbol_kind == "FUNCTION"
    assert source.language == "javascript"
    assert source.start_line == 1
    assert source.end_line == 3
    assert source.semantic_score == 0.9
    assert source.semantic_rank == 1
    assert source.graph_relations == ()

    assert llm_provider.last_question == "Where is user input validated?"

    assert llm_provider.last_context is not None

    assert "validationCheck" in llm_provider.last_context

    assert "function validationCheck" in llm_provider.last_context
    assert source.retrieval_origin == RetrievalOrigin.SEMANTIC

    assert result.retrieval_diagnostics.semantic_sources == 1

    assert result.retrieval_diagnostics.graph_sources == 0

    assert result.retrieval_diagnostics.both_sources == 0

    assert result.retrieval_diagnostics.final_context_items == 1

    assert source.final_score == 0.9


def test_answer_repository_question_rejects_empty_question() -> None:
    snapshot = Snapshot.create(
        repository_id=uuid4(),
        commit_sha="b" * 40,
        branch="main",
        remote_url="https://github.com/example/repo",
    ).mark_ready()

    snapshot_store = InMemorySnapshotStore()
    snapshot_store.save(snapshot)

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
        snapshot_store=snapshot_store,
    )

    with pytest.raises(ValueError):
        use_case.execute(
            snapshot_id=snapshot.id,
            question="   ",
        )


def test_answer_repository_question_rejects_unknown_snapshot() -> None:
    snapshot_store = InMemorySnapshotStore()

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
        snapshot_store=snapshot_store,
    )

    with pytest.raises(SnapshotNotFoundError):
        use_case.execute(
            snapshot_id=uuid4(),
            question="How is the application structured?",
        )
