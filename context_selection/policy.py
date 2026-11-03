
from collections import Counter

from context_selection.selection import select_context


def inspect_selection(result):
    """
    Generate an inspection report for a context-selection result.
    """

    selected = result["selected"]
    excluded = result["excluded"]

    all_items = selected + excluded

    source_counts = Counter(
        item["candidate"].source for item in selected
    )

    total_candidates = len(all_items)
    selected_count = len(selected)

    used_tokens = result["used_tokens"]
    budget = result["budget"]

    utilization = (
        round((used_tokens / budget) * 100, 2)
        if budget > 0 else 0.0
    )

    selection_rate = (
        round((selected_count / total_candidates) * 100, 2)
        if total_candidates > 0 else 0.0
    )

    average_score = (
        round(
            sum(item["score"] for item in selected)
            / selected_count,
            4
        )
        if selected_count else 0.0
    )

    return {
        "total_candidates": total_candidates,
        "selected_count": selected_count,
        "excluded_count": len(excluded),
        "used_tokens": used_tokens,
        "remaining_tokens": result["remaining_tokens"],
        "budget": budget,
        "budget_utilization_percent": utilization,
        "selection_rate_percent": selection_rate,
        "average_selected_score": average_score,
        "source_distribution": dict(source_counts)
    }


def compare_policies(
    candidates,
    budget,
    policies
):
    """
    Compare context selection under multiple scoring policies.
    """

    if not isinstance(policies, dict) or not policies:
        raise ValueError("At least one policy is required")

    results = {}

    for policy_name, configuration in policies.items():

        if not isinstance(policy_name, str) or not policy_name.strip():
            raise ValueError("Policy names must be non-empty strings")

        if not isinstance(configuration, dict):
            raise ValueError("Policy configuration must be a dictionary")

        allowed_keys = {"feature_weights", "source_weights"}

        if set(configuration) - allowed_keys:
            raise ValueError("Unknown policy configuration option")

        result = select_context(
            candidates,
            budget,
            feature_weights=configuration.get("feature_weights"),
            source_weights=configuration.get("source_weights")
        )

        selected_ids = [
            item["candidate"].candidate_id
            for item in result["selected"]
        ]

        results[policy_name] = {
            "selected_ids": selected_ids,
            "used_tokens": result["used_tokens"],
            "remaining_tokens": result["remaining_tokens"],
            "inspection": inspect_selection(result)
        }

    return results


def generate_inspection_report(result):
    """
    Generate a readable text report.
    """

    inspection = inspect_selection(result)

    lines = [
        "CONTEXT SELECTION INSPECTION REPORT",
        "=" * 45,
        f"Total candidates: {inspection['total_candidates']}",
        f"Selected: {inspection['selected_count']}",
        f"Excluded: {inspection['excluded_count']}",
        f"Token usage: {inspection['used_tokens']}/{inspection['budget']}",
        f"Remaining tokens: {inspection['remaining_tokens']}",
        f"Budget utilization: {inspection['budget_utilization_percent']}%",
        f"Selection rate: {inspection['selection_rate_percent']}%",
        f"Average selected score: {inspection['average_selected_score']}",
        "",
        "SOURCE DISTRIBUTION",
        "-" * 25
    ]

    for source, count in sorted(
        inspection["source_distribution"].items()
    ):
        lines.append(f"{source}: {count}")

    return "\n".join(lines)
