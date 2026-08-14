import os

import pytest

from codenerva.application.qa.answer_repository_question import (
    AnswerRepositoryQuestionUseCase,
)
from codenerva.application.retrieval.context_formatter import (
    ContextFormatter,
)
from codenerva.infrastructure.openai_llm_provider import (
    OpenAILLMProvider,
)
from tests.evaluation.fizz_fixture import (
    END_TO_END_QUESTION,
    INSUFFICIENT_CONTEXT_QUESTION,
    PARTIAL_EVIDENCE_QUESTION,
    STRUCTURE_QUESTION,
    TESTING_QUESTION,
    build_fizz_evaluation_fixture,
)
from tests.evaluation.llm_judge import (
    OpenAILLMJudge,
)

pytestmark = pytest.mark.llm_eval


def test_fizz_answer_with_llm_judge() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required for llm evaluation.")

    fixture = build_fizz_evaluation_fixture()

    answer_use_case = AnswerRepositoryQuestionUseCase(
        snapshot_store=fixture.snapshot_store,
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
        context_formatter=ContextFormatter(),
        llm_provider=OpenAILLMProvider(
            model="gpt-5-mini",
        ),
    )

    result = answer_use_case.execute(
        snapshot_id=fixture.snapshot_id,
        question=END_TO_END_QUESTION,
        top_k=4,
        max_items=8,
        max_chars=16000,
    )

    judge = OpenAILLMJudge(
        model="gpt-5-mini",
    )

    scores = judge.evaluate(
        question=END_TO_END_QUESTION,
        answer=result.answer,
        context=result.formatted_context,
        expected_facts=(
            "post_fizz calls FizzService.create",
            "get_fizz calls FizzService.get_all",
            "FizzService.create persists a Fizz model",
            "FizzService.get_all queries Fizz rows",
            "FizzSchema is used between the API and service layers",
        ),
    )
    print()
    print("LLM Judge scores")
    print(f"Correctness:  {scores.correctness:.3f}")
    print(f"Groundedness: {scores.groundedness:.3f}")
    print(f"Completeness: {scores.completeness:.3f}")
    print(f"Mean score:   {scores.mean_score:.3f}")

    assert scores.correctness >= 0.80
    assert scores.groundedness >= 0.85
    assert scores.completeness >= 0.75


def test_fizz_structure_with_llm_judge() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required for llm evaluation.")

    fixture = build_fizz_evaluation_fixture()

    answer_use_case = AnswerRepositoryQuestionUseCase(
        snapshot_store=fixture.snapshot_store,
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
        context_formatter=ContextFormatter(),
        llm_provider=OpenAILLMProvider(
            model="gpt-5-mini",
        ),
    )

    result = answer_use_case.execute(
        snapshot_id=fixture.snapshot_id,
        question=STRUCTURE_QUESTION,
        top_k=4,
        max_items=8,
        max_chars=16000,
    )

    judge = OpenAILLMJudge(
        model="gpt-5-mini",
    )

    scores = judge.evaluate(
        question=STRUCTURE_QUESTION,
        answer=result.answer,
        context=result.formatted_context,
        expected_facts=(
            "FizzService contains FizzService.create",
            "FizzService contains FizzService.get_all",
        ),
    )

    print()
    print("Structure judge scores")
    print(f"Correctness:  {scores.correctness:.3f}")
    print(f"Groundedness: {scores.groundedness:.3f}")
    print(f"Completeness: {scores.completeness:.3f}")
    print(f"Mean score:   {scores.mean_score:.3f}")

    assert scores.correctness >= 0.80
    assert scores.groundedness >= 0.85
    assert scores.completeness >= 0.75


def test_fizz_testing_with_llm_judge() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required for llm evaluation.")

    fixture = build_fizz_evaluation_fixture()

    answer_use_case = AnswerRepositoryQuestionUseCase(
        snapshot_store=fixture.snapshot_store,
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
        context_formatter=ContextFormatter(),
        llm_provider=OpenAILLMProvider(
            model="gpt-5-mini",
        ),
    )

    result = answer_use_case.execute(
        snapshot_id=fixture.snapshot_id,
        question=TESTING_QUESTION,
        top_k=4,
        max_items=8,
        max_chars=16000,
    )

    judge = OpenAILLMJudge(
        model="gpt-5-mini",
    )
    print()
    print("Testing answer:")
    print(result.answer)
    print()

    scores = judge.evaluate(
        question=TESTING_QUESTION,
        answer=result.answer,
        context=result.formatted_context,
        expected_facts=(
            "The Fizz model test helper is defined in app/fizz/model_test.py",
            "The fizz test helper creates a Fizz model",
        ),
    )

    print()
    print("Testing judge scores")
    print(f"Correctness:  {scores.correctness:.3f}")
    print(f"Groundedness: {scores.groundedness:.3f}")
    print(f"Completeness: {scores.completeness:.3f}")
    print(f"Mean score:   {scores.mean_score:.3f}")

    assert scores.correctness >= 0.80
    assert scores.groundedness >= 0.85
    assert scores.completeness >= 0.75


def test_fizz_insufficient_context_with_llm_judge() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required for llm evaluation.")

    fixture = build_fizz_evaluation_fixture()

    answer_use_case = AnswerRepositoryQuestionUseCase(
        snapshot_store=fixture.snapshot_store,
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
        context_formatter=ContextFormatter(),
        llm_provider=OpenAILLMProvider(
            model="gpt-5-mini",
        ),
    )

    question = INSUFFICIENT_CONTEXT_QUESTION

    result = answer_use_case.execute(
        snapshot_id=fixture.snapshot_id,
        question=question,
        top_k=4,
        max_items=8,
        max_chars=16000,
    )

    judge = OpenAILLMJudge(
        model="gpt-5-mini",
    )

    scores = judge.evaluate(
        question=question,
        answer=result.answer,
        context=result.formatted_context,
        expected_facts=(
            (
                "The provided repository context does not contain enough "
                "evidence to determine the authentication mechanism."
            ),
            (
                "The provided repository context does not contain enough "
                "evidence to determine how access tokens are validated."
            ),
        ),
    )

    print()
    print("Insufficient-context judge scores")
    print(f"Correctness:  {scores.correctness:.3f}")
    print(f"Groundedness: {scores.groundedness:.3f}")
    print(f"Completeness: {scores.completeness:.3f}")
    print(f"Mean score:   {scores.mean_score:.3f}")
    print()
    print("Answer:")
    print(result.answer)

    assert scores.correctness >= 0.80
    assert scores.groundedness >= 0.90
    assert scores.completeness >= 0.75


def test_fizz_partial_evidence_with_llm_judge() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY is required for llm evaluation.")

    fixture = build_fizz_evaluation_fixture()

    answer_use_case = AnswerRepositoryQuestionUseCase(
        snapshot_store=fixture.snapshot_store,
        hybrid_retrieval=fixture.hybrid_retrieval,
        hybrid_reranker=fixture.hybrid_reranker,
        context_builder=fixture.context_builder,
        context_formatter=ContextFormatter(),
        llm_provider=OpenAILLMProvider(
            model="gpt-5-mini",
        ),
    )

    question = PARTIAL_EVIDENCE_QUESTION

    result = answer_use_case.execute(
        snapshot_id=fixture.snapshot_id,
        question=question,
        top_k=4,
        max_items=8,
        max_chars=16000,
    )

    judge = OpenAILLMJudge(
        model="gpt-5-mini",
    )

    scores = judge.evaluate(
        question=question,
        answer=result.answer,
        context=result.formatted_context,
        expected_facts=(
            "FizzService.create creates a Fizz model from FizzSchema.",
            "FizzService.create adds the Fizz model to the database session.",
            "FizzService.create commits the database session.",
            (
                "The provided context does not establish what happens "
                "if the database commit fails."
            ),
        ),
    )

    print()
    print("Partial-evidence judge scores")
    print(f"Correctness:  {scores.correctness:.3f}")
    print(f"Groundedness: {scores.groundedness:.3f}")
    print(f"Completeness: {scores.completeness:.3f}")
    print(f"Mean score:   {scores.mean_score:.3f}")
    print()
    print("Answer:")
    print(result.answer)

    assert scores.correctness >= 0.80
    assert scores.groundedness >= 0.90
    assert scores.completeness >= 0.75
