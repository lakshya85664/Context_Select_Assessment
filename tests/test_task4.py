
import pytest

from context_selection.models import ContextCandidate
from context_selection.retrieval import (
    retrieve_vector_candidates,
    summarize_history,
    create_summary_candidate,
    collect_context_candidates,
    explain_selection
)
from context_selection.sample_data import create_sample_candidates
from context_selection.selection import select_context


def test_high_relevance_vector_retrieval():
    vector_store = create_sample_candidates()

    results = retrieve_vector_candidates(
        "Python programming",
        vector_store,
        min_relevance=9
    )

    assert len(results) == 1
    assert results[0].candidate_id == "VEC001"



def test_low_relevance_vector_excluded():
    vector_store = [
        ContextCandidate(
            candidate_id="VEC_LOW",
            text="Unrelated programming information.",
            source="vector",
            relevance=6,
            recency=5,
            priority=4,
            token_count=12
        )
    ]

    results = retrieve_vector_candidates(
        "Python programming",
        vector_store,
        min_relevance=9
    )

    assert results == []


def test_historical_summarization():
    history = [
        "User is learning Python.",
        "User prefers backend development.",
        "User completed an ML project.",
        "Older irrelevant conversation."
    ]

    summary = summarize_history(history, max_items=3)

    assert "Python" in summary
    assert "backend" in summary
    assert "ML project" in summary
    assert "irrelevant" not in summary


def test_summary_candidate_creation():
    history = [
        "User knows Python.",
        "User has machine learning experience."
    ]

    candidate = create_summary_candidate(history)

    assert candidate is not None
    assert candidate.candidate_id == "SUM001"
    assert candidate.source == "long_term"
    assert candidate.token_count > 0


def test_empty_history():
    candidate = create_summary_candidate([])

    assert candidate is None


def test_collect_all_context_sources():
    existing = create_sample_candidates()

    vector_store = [
        ContextCandidate(
            candidate_id="VEC002",
            text="Python functions and programming examples.",
            source="vector",
            relevance=9.5,
            recency=8,
            priority=9,
            token_count=10
        )
    ]

    history = [
        "User is learning Python.",
        "User prefers practical coding exercises."
    ]

    combined = collect_context_candidates(
        existing,
        vector_store,
        history,
        "Python"
    )

    sources = {candidate.source for candidate in combined}

    assert "short_term" in sources
    assert "long_term" in sources
    assert "vector" in sources

    ids = [candidate.candidate_id for candidate in combined]

    assert "VEC002" in ids
    assert "SUM001" in ids



def test_duplicate_candidate_ids_rejected():
    existing = create_sample_candidates()

    existing.append(
        ContextCandidate(
            candidate_id="SUM001",
            text="Existing summary",
            source="long_term",
            relevance=8,
            recency=5,
            priority=8,
            token_count=5
        )
    )

    with pytest.raises(ValueError):
        collect_context_candidates(
            existing,
            [],
            ["User knows Python."],
            "Python"
        )



def test_selection_explanations():
    candidates = create_sample_candidates()

    result = select_context(candidates, budget=40)

    explanations = explain_selection(result)

    selected = [
        item for item in explanations
        if item["decision"] == "selected"
    ]

    excluded = [
        item for item in explanations
        if item["decision"] == "excluded"
    ]

    assert len(selected) == 3
    assert len(excluded) == 2

    assert all(item["reason"] for item in explanations)


def test_invalid_query():
    with pytest.raises(ValueError):
        retrieve_vector_candidates(
            "",
            create_sample_candidates()
        )


def test_invalid_summary_limit():
    with pytest.raises(ValueError):
        summarize_history(
            ["User knows Python."],
            max_items=0
        )
