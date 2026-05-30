# Personal n8n QA Agent

Version 1 is a personal Telegram-controlled QA agent for one self-hosted n8n workflow.

## What it does

- Receives `test <workflow name>` and `report <latest|run_id>` from Telegram
- Creates four role-based QA scenarios
- Inspects n8n through API access plus browser screenshots
- Supports webhook-triggered workflows in the current version
- Stores runs, scenarios, evidence, and reports in PostgreSQL
- Sends a detailed QA report back to Telegram
- Never edits workflows in v1

## Quick start

1. Copy `.env.example` to `.env` and fill the values.
2. Start PostgreSQL:
   ```bash
   docker compose up -d
   ```
3. Install dependencies in a Python 3.11+ environment:
   ```bash
   pip install -e .[dev]
   playwright install chromium
   ```
4. Create the database tables:
   ```bash
   python -m qa_agent.db
   ```
5. Run the bot:
   ```bash
   python -m qa_agent.main
   ```

## Commands

- `test My Workflow`
- `report latest`
- `report <run_id>`

## Notes

- `browser-use` is included for future exploratory browsing; v1 browser work is implemented with Playwright for repeatability.
- Model providers are swappable through `MODEL_PROVIDER`. The code now supports `gemini`, `openai`, `anthropic`, and `groq`.
- Automatic execution in the current version works for workflows with an n8n Webhook trigger.
- Future versions will support additional n8n trigger nodes. Other workflow types are currently inspected and reported, but marked as not yet automatically executable rather than falsely marked as tested.
