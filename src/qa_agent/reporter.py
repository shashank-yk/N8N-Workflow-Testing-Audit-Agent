from __future__ import annotations

from .models import ScenarioResult


def build_recommendations(results: list[ScenarioResult]) -> list[str]:
    recommendations: list[str] = []
    for result in results:
        if result.status.value == "failed" and result.suspected_issue:
            if result.suspected_issue not in recommendations:
                recommendations.append(result.suspected_issue)
    return recommendations
