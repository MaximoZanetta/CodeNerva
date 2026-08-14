from tests.evaluation.evaluation_case import (
    RetrievalEvaluationCase,
)
from tests.evaluation.fizz_fixture import (
    END_TO_END_QUESTION,
    STRUCTURE_QUESTION,
    TESTING_QUESTION,
)

FIZZ_RETRIEVAL_CASES = (
    RetrievalEvaluationCase(
        name="fizz_end_to_end_flow",
        question=END_TO_END_QUESTION,
        expected_symbols=(
            "post_fizz",
            "get_fizz",
            "FizzService.create",
            "FizzService.get_all",
        ),
        minimum_recall=1.0,
        minimum_precision=0.50,
        minimum_mrr=0.50,
        minimum_ndcg=0.70,
    ),
    RetrievalEvaluationCase(
        name="fizz_service_structure",
        question=STRUCTURE_QUESTION,
        expected_symbols=(
            "FizzService.create",
            "FizzService.get_all",
        ),
        minimum_recall=1.0,
        minimum_precision=0.40,
        minimum_mrr=0.50,
        minimum_ndcg=0.70,
    ),
    RetrievalEvaluationCase(
        name="fizz_testing",
        question=TESTING_QUESTION,
        expected_symbols=("fizz",),
        minimum_recall=1.0,
        minimum_precision=0.20,
        minimum_mrr=0.25,
        minimum_ndcg=0.50,
    ),
)
