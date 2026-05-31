# Project Architecture

This project is a Python-based AI QA agent that tests and audits n8n workflows through Telegram commands.

The system is designed as a safe workflow-inspection assistant. Version 1 focuses on testing, reporting, and improvement suggestions. It does not directly edit or modify n8n workflows.

---

## High-Level Runtime Flow

```text
User
 ↓
Telegram Bot
 ↓
Main QA Agent
 ↓
n8n API Client
 ↓
Workflow Inspection
 ↓
Scenario Builder
 ↓
Scenario Execution
 ↓
Evidence Collection
 ↓
PostgreSQL Storage
 ↓
Report Generator
 ↓
Telegram Response
```

---

## Step-by-Step Flow

1. The user sends a Telegram command such as `test <workflow name>`.
2. The Telegram bot receives the command and passes it to the main QA flow.
3. The n8n client connects to the n8n API and loads the requested workflow.
4. The agent inspects workflow nodes, triggers, connections, and workflow purpose.
5. The QA flow creates role-based testing scenarios.
6. Supported workflows are executed using webhook/API logic.
7. Browser evidence can be captured using Playwright when needed.
8. Test run details, scenario results, and report data are saved to PostgreSQL.
9. The report generator creates a structured QA summary.
10. The final report is sent back to the user through Telegram.

---

## Main Components

| Component | Purpose |
|---|---|
| `src/qa_agent/main.py` | Starts the application, initializes services, and runs the Telegram bot. |
| `src/qa_agent/telegram_bot.py` | Handles Telegram commands and sends reports to users. |
| `src/qa_agent/qa_flow.py` | Coordinates the end-to-end QA workflow. |
| `src/qa_agent/n8n_client.py` | Connects to n8n and triggers supported workflows. |
| `src/qa_agent/browser_client.py` | Uses Playwright for browser-based evidence collection. |
| `src/qa_agent/scenarios.py` | Defines role-based QA test scenarios. |
| `src/qa_agent/models.py` | Contains Pydantic models for workflows, scenarios, results, and reports. |
| `src/qa_agent/db.py` | Stores test runs, results, and reports in PostgreSQL. |
| `src/qa_agent/llm.py` | Provides model adapters for Gemini, OpenAI, Anthropic, and Groq. |

---

## Scenario Design

The project uses four role-based scenarios to test workflows from different perspectives:

1. **Customer scenario** – Tests normal user or lead-submission behaviour.
2. **Sales scenario** – Tests missing, incomplete, or lead-related edge cases.
3. **Manager scenario** – Tests decision-making, validation, and reporting behaviour.
4. **Admin scenario** – Tests duplicate, invalid, or operational edge cases.

This structure helps the agent find issues that may not appear in only one normal test run.

---

## Supported Workflow Types

### Fully Supported in Current Version

- n8n workflows using a **Webhook Trigger**.

### Partially Supported

- Manual-trigger workflows may have partial browser-based support.

### Inspection-Only Support

- Schedule triggers
- Google Sheets triggers
- Google Calendar triggers
- Gmail triggers
- Other app-specific triggers

For unsupported trigger types, the agent can still inspect the workflow and report limitations, but it does not falsely claim that the workflow was fully executed.

---

## Data Storage

PostgreSQL stores:

- test run IDs
- workflow metadata
- scenario results
- generated report markdown
- structured report payloads

Generated screenshots are written to the configured screenshot directory and are ignored by Git by default.

---

## Safety Design

Version 1 is intentionally read-focused and report-focused.

The agent can:

- inspect workflows
- run supported tests
- capture evidence
- generate reports
- suggest improvements

The agent does not:

- automatically edit workflows
- delete nodes
- change production logic
- auto-fix workflows without approval

This makes the project safer for real-world workflow auditing.
