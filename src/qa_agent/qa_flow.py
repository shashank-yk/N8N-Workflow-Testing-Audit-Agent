from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from langgraph.graph import END, START, StateGraph
from typing_extensions import TypedDict

from .browser_client import BrowserClient
from .llm import LlmAdapter
from .models import QaReport, ScenarioResult, ScenarioStatus, TestScenario, WorkflowSummary
from .n8n_client import N8nClient
from .reporter import build_recommendations
from .scenarios import build_role_scenarios


class QaState(TypedDict):
    workflow_name: str
    workflow: WorkflowSummary
    scenarios: list[TestScenario]
    results: list[ScenarioResult]
    run_id: str
    report: QaReport


class QaFlow:
    def __init__(self, n8n_client: N8nClient, browser_client: BrowserClient, llm: LlmAdapter | None = None) -> None:
        self.n8n = n8n_client
        self.browser = browser_client
        self.llm = llm
        graph = StateGraph(QaState)
        graph.add_node("load_workflow", self.load_workflow)
        graph.add_node("build_scenarios", self.make_scenarios)
        graph.add_node("run_scenarios", self.run_scenarios)
        graph.add_node("build_report", self.make_report)
        graph.add_edge(START, "load_workflow")
        graph.add_edge("load_workflow", "build_scenarios")
        graph.add_edge("build_scenarios", "run_scenarios")
        graph.add_edge("run_scenarios", "build_report")
        graph.add_edge("build_report", END)
        self.graph = graph.compile()

    async def run(self, workflow_name: str) -> QaReport:
        state = await self.graph.ainvoke({"workflow_name": workflow_name, "run_id": str(uuid4())})
        return state["report"]

    async def load_workflow(self, state: QaState) -> dict:
        workflow = await self.n8n.find_workflow_by_name(state["workflow_name"])
        return {"workflow": workflow}

    async def make_scenarios(self, _: QaState) -> dict:
        return {"scenarios": build_role_scenarios()}

    async def run_scenarios(self, state: QaState) -> dict:
        results: list[ScenarioResult] = []
        for scenario in state["scenarios"]:
            response = await self.n8n.trigger_webhook(state["workflow"], scenario.input_payload)
            screenshot_path = self.browser.screenshot_path(
                run_id=state["run_id"],
                role=scenario.role.value,
            )
            if response is None and state["workflow"].has_manual_trigger:
                try:
                    await self.browser.execute_manual_workflow(state["workflow"].id, screenshot_path=screenshot_path)
                    latest_execution = await self.n8n.get_latest_execution(state["workflow"].id)
                    if latest_execution:
                        execution_log = latest_execution
                        if latest_execution.get("id"):
                            try:
                                execution_log = await self.n8n.get_execution(str(latest_execution["id"]))
                            except Exception:
                                execution_log = latest_execution
                        response = None
                        status = ScenarioStatus.PASSED if execution_log.get("status") != "error" else ScenarioStatus.FAILED
                        issue = None if status == ScenarioStatus.PASSED else self._summarize_execution_error(execution_log)
                        actual = f"Manual execution completed with status: {latest_execution.get('status', 'unknown')}."
                        results.append(
                            ScenarioResult(
                                scenario=scenario,
                                status=status,
                                actual_behavior=actual,
                                suspected_issue=issue,
                                screenshot_path=str(screenshot_path),
                                execution_log=execution_log,
                            )
                        )
                        continue
                except Exception as exc:
                    results.append(
                        ScenarioResult(
                            scenario=scenario,
                            status=ScenarioStatus.ERROR,
                            actual_behavior="Manual trigger detected, but the browser could not click the run button.",
                            suspected_issue=f"Manual execution adapter failed: {exc}",
                            screenshot_path=str(screenshot_path),
                            execution_log=None,
                        )
                    )
                    continue
            screenshot = await self.browser.capture_workflow_screenshot(
                workflow_id=state["workflow"].id,
                run_id=state["run_id"],
                role=scenario.role.value,
            )
            latest_execution = await self.n8n.get_latest_execution(state["workflow"].id)
            if response is None:
                status = ScenarioStatus.ERROR
                issue = (
                    "No webhook trigger found. This workflow should be tested through a trigger-specific adapter, "
                    f"not by changing its trigger. Detected trigger(s): {state['workflow'].trigger_summary}."
                )
                actual = "Browser evidence captured, but automatic execution adapter is not implemented for this trigger type yet."
            elif response.is_success:
                status = ScenarioStatus.PASSED
                issue = None
                actual = f"Webhook returned HTTP {response.status_code}."
            else:
                status = ScenarioStatus.FAILED
                issue = f"Webhook returned HTTP {response.status_code}; inspect branch handling for {scenario.title}."
                actual = response.text[:500]
            results.append(
                ScenarioResult(
                    scenario=scenario,
                    status=status,
                    actual_behavior=actual,
                    suspected_issue=issue,
                    screenshot_path=screenshot,
                    execution_log=latest_execution,
                )
            )
        return {"results": results}

    def _summarize_execution_error(self, execution: dict) -> str:
        error = execution.get("data", {}).get("resultData", {}).get("error", {})
        node = error.get("node", {}).get("name")
        message = error.get("message")
        if node and message:
            return f'Failed at "{node}": {message}'
        if message:
            return message
        return "Manual execution ended with an error, but n8n did not return node-level error details."

    async def make_report(self, state: QaState) -> dict:
        passed = [item for item in state["results"] if item.status == ScenarioStatus.PASSED]
        failed = [item for item in state["results"] if item.status != ScenarioStatus.PASSED]
        recommendations = build_recommendations(failed)
        if self.llm and failed:
            prompt = (
                "You are a QA reviewer. Rewrite these raw recommendations into a concise numbered list "
                "for a non-technical owner. Keep each item under 20 words.\n\n"
                + "\n".join(f"- {item}" for item in recommendations)
            )
            try:
                llm_text = await self.llm.complete(prompt)
                llm_recommendations = [
                    line.strip(" -")
                    for line in llm_text.splitlines()
                    if line.strip()
                ]
                if llm_recommendations:
                    recommendations = llm_recommendations
            except Exception:
                pass
        report = QaReport(
            run_id=state["run_id"],
            workflow=state["workflow"],
            created_at=datetime.utcnow(),
            passed=passed,
            failed=failed,
            recommendations=recommendations,
        )
        return {"report": report}
