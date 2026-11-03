
import pytest

from context_selection.selection import select_context
from context_selection.sample_data import create_sample_candidates


def test_selection_with_budget():
    candidates = create_sample_candidates()

    result = select_context(candidates, budget=40)

    selected_ids = [
        item["candidate"].candidate_id
        for item in result["selected"]
    ]

    assert selected_ids == [
        "VEC001",
        "STM001",
        "LTM001"
    ]

    assert result["used_tokens"] == 38
    assert result["remaining_tokens"] == 2


def test_empty_candidate_list():
    result = select_context([], budget=100)

    assert result["selected"] == []
    assert result["excluded"] == []
    assert result["used_tokens"] == 0
    assert result["remaining_tokens"] == 100


def test_candidate_exceeding_budget():
    candidates = create_sample_candidates()

    result = select_context(candidates, budget=10)

    assert result["selected"] == []

    assert len(result["excluded"]) == 5

    assert result["used_tokens"] == 0


def test_exact_budget_boundary():
    candidates = create_sample_candidates()

    result = select_context(candidates, budget=38)

    assert result["used_tokens"] == 38
    assert result["remaining_tokens"] == 0

    assert len(result["selected"]) == 3


def test_selection_never_exceeds_budget():
    candidates = create_sample_candidates()

    for budget in [10, 20, 30, 40, 50, 100]:
        result = select_context(candidates, budget)

        assert result["used_tokens"] <= budget



def test_skip_large_candidate_and_continue():
    candidates = create_sample_candidates()

    result = select_context(candidates, budget=26)

    selected_ids = [
        item["candidate"].candidate_id
        for item in result["selected"]
    ]

    assert selected_ids == [
        "VEC001",
        "LTM001"
    ]

    assert result["used_tokens"] == 26
    assert result["remaining_tokens"] == 0



def test_invalid_budget():
    candidates = create_sample_candidates()

    with pytest.raises(ValueError):
        select_context(candidates, budget=-10)


def test_budget_must_be_integer():
    candidates = create_sample_candidates()

    with pytest.raises(ValueError):
        select_context(candidates, budget=10.5)
