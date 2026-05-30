from qa_agent.models import Role, ScenarioResult, ScenarioStatus, TestScenario
from qa_agent.reporter import build_recommendations


def test_build_recommendations_uses_failed_issues_only():
    scenario = TestScenario(
        role=Role.ADMIN,
        title="duplicate submission",
        input_payload={},
        expected_behavior="safe handling",
    )
    recommendations = build_recommendations(
        [
            ScenarioResult(
                scenario=scenario,
                status=ScenarioStatus.FAILED,
                actual_behavior="bad",
                suspected_issue="Add deduplication.",
            ),
            ScenarioResult(
                scenario=scenario,
                status=ScenarioStatus.PASSED,
                actual_behavior="ok",
                suspected_issue="Ignore me.",
            ),
        ]
    )
    assert recommendations == ["Add deduplication."]
