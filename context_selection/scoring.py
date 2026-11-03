
from math import isclose, isfinite

from context_selection.models import ContextCandidate


# Configurable feature weights
DEFAULT_FEATURE_WEIGHTS = {
    "relevance": 0.50,
    "recency": 0.20,
    "priority": 0.30
}


# Configurable source weights
DEFAULT_SOURCE_WEIGHTS = {
    "short_term": 1.00,
    "long_term": 0.95,
    "vector": 1.05
}


def validate_weights(feature_weights, source_weights, source):
    """Validate scoring configuration."""

    required_features = {
        "relevance",
        "recency",
        "priority"
    }

    if set(feature_weights) != required_features:
        raise ValueError("Invalid feature weight configuration")

    for weight in feature_weights.values():
        if (
            isinstance(weight, bool)
            or not isinstance(weight, (int, float))
            or not isfinite(weight)
            or weight < 0
        ):
            raise ValueError("Feature weights must be finite and non-negative")

    if not isclose(sum(feature_weights.values()), 1.0):
        raise ValueError("Feature weights must sum to 1.0")

    if source not in source_weights:
        raise ValueError("Missing source weight")

    source_weight = source_weights[source]

    if (
        isinstance(source_weight, bool)
        or not isinstance(source_weight, (int, float))
        or not isfinite(source_weight)
        or source_weight <= 0
    ):
        raise ValueError("Source weight must be positive and finite")


def calculate_score(
    candidate: ContextCandidate,
    feature_weights=None,
    source_weights=None
):
    """
    Calculate a candidate's weighted context score.

    Formula:
    (relevance * weight +
     recency * weight +
     priority * weight) * source_weight
    """

    feature_weights = (
        DEFAULT_FEATURE_WEIGHTS.copy()
        if feature_weights is None
        else feature_weights
    )

    source_weights = (
        DEFAULT_SOURCE_WEIGHTS.copy()
        if source_weights is None
        else source_weights
    )

    validate_weights(
        feature_weights,
        source_weights,
        candidate.source
    )

    base_score = (
        candidate.relevance * feature_weights["relevance"]
        + candidate.recency * feature_weights["recency"]
        + candidate.priority * feature_weights["priority"]
    )

    final_score = base_score * source_weights[candidate.source]

    return round(final_score, 4)


def rank_candidates(
    candidates,
    feature_weights=None,
    source_weights=None
):
    """
    Rank candidates from highest to lowest score.

    Tie-breaking:
    1. Higher relevance first.
    2. Candidate ID in ascending alphabetical order.
    """

    scored_candidates = [
        (
            candidate,
            calculate_score(
                candidate,
                feature_weights,
                source_weights
            )
        )
        for candidate in candidates
    ]

    return sorted(
        scored_candidates,
        key=lambda item: (
            -item[1],
            -item[0].relevance,
            item[0].candidate_id
        )
    )
