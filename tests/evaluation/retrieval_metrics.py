import math
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetrievalMetrics:
    recall: float
    precision: float
    hit_rate: float
    mrr: float
    ndcg: float

    expected_count: int
    retrieved_count: int
    relevant_retrieved_count: int


def evaluate_retrieval(
    *,
    expected_symbols: tuple[str, ...],
    retrieved_symbols: tuple[str, ...],
) -> RetrievalMetrics:
    expected = set(expected_symbols)
    retrieved = set(retrieved_symbols)

    if not expected:
        raise ValueError("expected_symbols cannot be empty.")

    relevant_retrieved = expected & retrieved

    recall = len(relevant_retrieved) / len(expected)

    precision = len(relevant_retrieved) / len(retrieved) if retrieved else 0.0

    hit_rate = 1.0 if relevant_retrieved else 0.0

    mrr = _mean_reciprocal_rank(
        expected_symbols=expected,
        retrieved_symbols=retrieved_symbols,
    )

    ndcg = _normalized_discounted_cumulative_gain(
        expected_symbols=expected,
        retrieved_symbols=retrieved_symbols,
    )

    return RetrievalMetrics(
        recall=recall,
        precision=precision,
        hit_rate=hit_rate,
        mrr=mrr,
        ndcg=ndcg,
        expected_count=len(expected),
        retrieved_count=len(retrieved),
        relevant_retrieved_count=(len(relevant_retrieved)),
    )


def _mean_reciprocal_rank(
    *,
    expected_symbols: set[str],
    retrieved_symbols: tuple[str, ...],
) -> float:
    for rank, symbol in enumerate(
        retrieved_symbols,
        start=1,
    ):
        if symbol in expected_symbols:
            return 1.0 / rank

    return 0.0


def _normalized_discounted_cumulative_gain(
    *,
    expected_symbols: set[str],
    retrieved_symbols: tuple[str, ...],
) -> float:
    dcg = 0.0

    for rank, symbol in enumerate(
        retrieved_symbols,
        start=1,
    ):
        if symbol not in expected_symbols:
            continue

        dcg += 1.0 / math.log2(rank + 1)

    ideal_relevant_count = min(
        len(expected_symbols),
        len(retrieved_symbols),
    )

    if ideal_relevant_count == 0:
        return 0.0

    ideal_dcg = sum(
        1.0 / math.log2(rank + 1)
        for rank in range(
            1,
            ideal_relevant_count + 1,
        )
    )

    return dcg / ideal_dcg
