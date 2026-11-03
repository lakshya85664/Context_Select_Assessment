
import pytest

from context_selection.models import ContextCandidate
from context_selection.sample_data import create_sample_candidates


def test_candidate_model_creation():
    candidate = ContextCandidate(
        candidate_id="TEST001",
        text="Learning Python",
        source="short_term",
        relevance=9,
        recency=8,
        priority=7,
        token_count=10
    )

    assert candidate.candidate_id == "TEST001"
    assert candidate.source == "short_term"
    assert candidate.relevance == 9


def test_all_memory_sources_included():
    candidates = create_sample_candidates()

    sources = {candidate.source for candidate in candidates}

    assert sources == {
        "short_term",
        "long_term",
        "vector"
    }


def test_candidate_numeric_ranges():
    with pytest.raises(ValueError):
        ContextCandidate(
            candidate_id="TEST002",
            text="Invalid relevance",
            source="short_term",
            relevance=11,
            recency=8,
            priority=7,
            token_count=10
        )


def test_invalid_source_rejected():
    with pytest.raises(ValueError):
        ContextCandidate(
            candidate_id="TEST003",
            text="Invalid source",
            source="unknown",
            relevance=8,
            recency=8,
            priority=7,
            token_count=10
        )


def test_invalid_token_count_rejected():
    with pytest.raises(ValueError):
        ContextCandidate(
            candidate_id="TEST004",
            text="Invalid token count",
            source="vector",
            relevance=8,
            recency=8,
            priority=7,
            token_count=0
        )


def test_sample_candidates_are_deterministic():
    first = create_sample_candidates()
    second = create_sample_candidates()

    assert first == second
