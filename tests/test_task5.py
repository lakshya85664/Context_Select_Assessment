
import pytest

from context_selection.sample_data import create_sample_candidates
from context_selection.selection import select_context
from context_selection.policy import (
    inspect_selection,
    compare_policies,
    generate_inspection_report
)


def test_inspection_candidate_counts():
    result = select_context(
        create_sample_candidates(),
        budget=40
    )

    report = inspect_selection(result)

    assert report["total_candidates"] == 5
    assert report["selected_count"] == 3
    assert report["excluded_count"] == 2


def test_budget_utilization():
    result = select_context(
        create_sample_candidates(),
        budget=40
    )

    report = inspect_selection(result)

    assert report["used_tokens"] == 38
    assert report["remaining_tokens"] == 2
    assert report["budget_utilization_percent"] == 95.0


def test_source_distribution():
    result = select_context(
        create_sample_candidates(),
        budget=40
    )

    report = inspect_selection(result)

    assert report["source_distribution"] == {
        "vector": 1,
        "short_term": 1,
        "long_term": 1
    }


def test_selection_rate():
    result = select_context(
        create_sample_candidates(),
        budget=40
    )

    report = inspect_selection(result)

    assert report["selection_rate_percent"] == 60.0


def test_average_selected_score():
    result = select_context(
        create_sample_candidates(),
        budget=40
    )

    report = inspect_selection(result)

    expected = round(
        (8.925 + 8.9 + 7.505) / 3,
        4
    )

    assert report["average_selected_score"] == expected


def test_compare_different_policies():
    candidates = create_sample_candidates()

    policies = {
        "default": {},
        "recency_focused": {
            "feature_weights": {
                "relevance": 0.20,
                "recency": 0.60,
                "priority": 0.20
            }
        }
    }

    results = compare_policies(
        candidates,
        budget=40,
        policies=policies
    )

    assert "default" in results
    assert "recency_focused" in results

    assert results["default"]["used_tokens"] <= 40
    assert results["recency_focused"]["used_tokens"] <= 40


def test_empty_selection_inspection():
    result = select_context([], budget=100)

    report = inspect_selection(result)

    assert report["total_candidates"] == 0
    assert report["selected_count"] == 0
    assert report["selection_rate_percent"] == 0.0
    assert report["average_selected_score"] == 0.0


def test_inspection_report_generation():
    result = select_context(
        create_sample_candidates(),
        budget=40
    )

    report = generate_inspection_report(result)

    assert "CONTEXT SELECTION INSPECTION REPORT" in report
    assert "Budget utilization: 95.0%" in report
    assert "SOURCE DISTRIBUTION" in report


def test_invalid_policy_configuration():
    with pytest.raises(ValueError):
        compare_policies(
            create_sample_candidates(),
            budget=40,
            policies={}
        )


def test_unknown_policy_option():
    with pytest.raises(ValueError):
        compare_policies(
            create_sample_candidates(),
            budget=40,
            policies={
                "invalid": {
                    "unknown_option": True
                }
            }
        )
