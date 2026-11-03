
import pytest

from context_selection.models import ContextCandidate
from context_selection.sample_data import create_sample_candidates
from context_selection.scoring import (
    calculate_score,
    rank_candidates,
    DEFAULT_FEATURE_WEIGHTS
)


def test_default_scoring_formula():
    candidate = create_sample_candidates()[0]

    score = calculate_score(candidate)

    assert score == 8.9


def test_source_weighting():
    candidate = create_sample_candidates()[2]

    score = calculate_score(candidate)

    assert score == 8.925


def test_configurable_feature_weights():
    candidate = create_sample_candidates()[0]

    custom_weights = {
        "relevance": 0.60,
        "recency": 0.20,
        "priority": 0.20
    }

    score = calculate_score(
        candidate,
        feature_weights=custom_weights
    )

    assert score == 9.0


def test_ranking_highest_score_first():
    candidates = create_sample_candidates()

    ranked = rank_candidates(candidates)

    scores = [score for candidate, score in ranked]

    assert scores == sorted(scores, reverse=True)


def test_ranking_is_deterministic():
    candidates = create_sample_candidates()

    first = rank_candidates(candidates)
    second = rank_candidates(candidates)

    assert first == second


def test_empty_candidate_list():
    assert rank_candidates([]) == []


def test_invalid_feature_weights():
    candidate = create_sample_candidates()[0]

    invalid_weights = {
        "relevance": 0.50,
        "recency": 0.20,
        "priority": 0.20
    }

    with pytest.raises(ValueError):
        calculate_score(
            candidate,
            feature_weights=invalid_weights
        )


def test_custom_source_weights():
    candidate = create_sample_candidates()[0]

    custom_sources = {
        "short_term": 1.20,
        "long_term": 0.90,
        "vector": 1.00
    }

    score = calculate_score(
        candidate,
        source_weights=custom_sources
    )

    assert score == 10.68
