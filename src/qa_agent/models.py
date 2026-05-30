from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Role(StrEnum):
    CUSTOMER = "customer"
    SALES = "sales"
    MANAGER = "manager"
    ADMIN = "admin"


class ScenarioStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


class WorkflowSummary(BaseModel):
    id: str
    name: str
    active: bool = False
    nodes: list[dict] = Field(default_factory=list)

    @property
    def trigger_nodes(self) -> list[dict]:
        return [
            node
            for node in self.nodes
            if "trigger" in str(node.get("type", "")).lower()
            or str(node.get("type", "")).lower().endswith(".webhook")
        ]

    @property
    def webhook_trigger(self) -> dict | None:
        for node in self.nodes:
            if node.get("type") == "n8n-nodes-base.webhook":
                return node
        return None

    @property
    def has_manual_trigger(self) -> bool:
        return any("manual" in str(node.get("type", "")).lower() for node in self.trigger_nodes)

    @property
    def trigger_summary(self) -> str:
        if not self.trigger_nodes:
            return "No trigger node detected"
        return ", ".join(node.get("type", "unknown") for node in self.trigger_nodes)


class TestScenario(BaseModel):
    role: Role
    title: str
    input_payload: dict
    expected_behavior: str


class ScenarioResult(BaseModel):
    scenario: TestScenario
    status: ScenarioStatus
    actual_behavior: str
    suspected_issue: str | None = None
    screenshot_path: str | None = None
    execution_log: dict | None = None


class QaReport(BaseModel):
    run_id: str
    workflow: WorkflowSummary
    created_at: datetime
    passed: list[ScenarioResult]
    failed: list[ScenarioResult]
    recommendations: list[str]

    def to_markdown(self) -> str:
        blocked = [item for item in self.failed if item.status == ScenarioStatus.ERROR]
        failed = [item for item in self.failed if item.status == ScenarioStatus.FAILED]
        lines = [
            f"# QA Report: {self.workflow.name}",
            f"Run ID: `{self.run_id}`",
            f"Created: {self.created_at.isoformat()}",
            "",
            f"Passed: {len(self.passed)}",
            f"Failed: {len(failed)}",
            f"Blocked: {len(blocked)}",
            "",
            "## Passed scenarios",
        ]
        if self.passed:
            lines.extend(f"- {item.scenario.role.value}: {item.scenario.title}" for item in self.passed)
        else:
            lines.append("- None")
        lines.append("")
        lines.append("## Failed scenarios")
        if failed:
            for item in failed:
                lines.append(
                    f"- {item.scenario.role.value}: {item.scenario.title} — {item.suspected_issue or item.actual_behavior}"
                )
        else:
            lines.append("- None")
        lines.append("")
        lines.append("## Blocked scenarios")
        if blocked:
            for item in blocked:
                lines.append(
                    f"- {item.scenario.role.value}: {item.scenario.title} — {item.suspected_issue or item.actual_behavior}"
                )
        else:
            lines.append("- None")
        lines.append("")
        lines.append("## Recommendations")
        if self.recommendations:
            lines.extend(f"- {item}" for item in self.recommendations)
        else:
            lines.append("- No changes recommended.")
        return "\n".join(lines)
