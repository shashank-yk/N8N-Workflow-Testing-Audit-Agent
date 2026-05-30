from datetime import datetime

from qa_agent.models import QaReport, Role, ScenarioResult, ScenarioStatus, TestScenario, WorkflowSummary


def test_report_markdown_contains_core_sections():
    scenario = TestScenario(
        role=Role.CUSTOMER,
        title="happy path",
        input_payload={},
        expected_behavior="success",
    )
    result = ScenarioResult(
        scenario=scenario,
        status=ScenarioStatus.PASSED,
        actual_behavior="ok",
    )
    report = QaReport(
        run_id="run-1",
        workflow=WorkflowSummary(id="1", name="Lead Flow"),
        created_at=datetime(2026, 5, 15),
        passed=[result],
        failed=[],
        recommendations=[],
    )
    markdown = report.to_markdown()
    assert "QA Report: Lead Flow" in markdown
    assert "Passed scenarios" in markdown
    assert "Recommendations" in markdown
