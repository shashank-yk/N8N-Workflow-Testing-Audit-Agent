# Project Architecture

This project is a Python-based QA agent for testing n8n workflows from Telegram.

## Runtime Flow

1. A user sends `test <workflow name>` to the Telegram bot.
2. The bot loads the workflow from n8n using the n8n API.
3. The QA flow builds four role-based scenarios: customer, sales, manager, and admin.
4. The agent runs each scenario against the workflow.
5. Browser evidence is captured with Playwright.
6. A QA report is generated and saved to PostgreSQL.
7. The report is returned to the Telegram chat.

## Main Components

- `src/qa_agent/main.py` starts the application, initializes the database, builds clients, and starts Telegram polling.
- `src/qa_agent/telegram_bot.py` handles Telegram commands and sends reports back to users.
- `src/qa_agent/qa_flow.py` coordinates the end-to-end QA workflow with LangGraph.
- `src/qa_agent/n8n_client.py` talks to the n8n API and triggers webhook workflows.
- `src/qa_agent/browser_client.py` uses Playwright to open n8n and capture screenshots.
- `src/qa_agent/scenarios.py` defines the built-in test scenarios.
- `src/qa_agent/models.py` contains the Pydantic data models for workflows, scenarios, results, and reports.
- `src/qa_agent/db.py` stores test runs and report data in PostgreSQL.
- `src/qa_agent/llm.py` provides model adapters for Gemini, OpenAI-compatible APIs, Anthropic, and Groq.

## Supported Workflow Types

The current version automatically executes n8n workflows with a Webhook trigger.

Manual-trigger workflows have partial browser-based support. Other trigger types are inspected and reported, but marked as not yet automatically executable.

## Data Storage

PostgreSQL stores:

- test run IDs
- workflow metadata
- scenario results
- generated report markdown
- structured report payloads

Generated screenshots are written to the configured screenshot directory and are ignored by Git by default.
