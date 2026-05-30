from __future__ import annotations

import httpx

from .config import settings
from .models import WorkflowSummary


class N8nClient:
    def __init__(self) -> None:
        headers = {}
        if settings.n8n_api_key:
            headers["X-N8N-API-KEY"] = settings.n8n_api_key
        self.client = httpx.AsyncClient(base_url=settings.n8n_base_url, headers=headers, timeout=30)

    async def close(self) -> None:
        await self.client.aclose()

    async def find_workflow_by_name(self, workflow_name: str) -> WorkflowSummary:
        response = await self.client.get("/api/v1/workflows")
        response.raise_for_status()
        workflows = response.json().get("data", [])
        for workflow in workflows:
            if workflow["name"].lower() == workflow_name.lower():
                return WorkflowSummary(
                    id=str(workflow["id"]),
                    name=workflow["name"],
                    active=workflow.get("active", False),
                    nodes=workflow.get("nodes", []),
                )
        raise ValueError(f"Workflow not found: {workflow_name}")

    async def get_latest_execution(self, workflow_id: str) -> dict | None:
        response = await self.client.get("/api/v1/executions", params={"workflowId": workflow_id, "limit": 1})
        response.raise_for_status()
        data = response.json().get("data", [])
        return data[0] if data else None

    async def get_execution(self, execution_id: str) -> dict:
        response = await self.client.get(f"/api/v1/executions/{execution_id}", params={"includeData": "true"})
        response.raise_for_status()
        return response.json()

    async def trigger_webhook(self, workflow: WorkflowSummary, payload: dict) -> httpx.Response | None:
        node = workflow.webhook_trigger
        if not node:
            return None
        parameters = node.get("parameters", {})
        path = parameters.get("path")
        if not path:
            return None
        method = str(parameters.get("httpMethod", "POST")).upper()
        url = f"/webhook/{path}"
        return await self.client.request(method, url, json=payload)
