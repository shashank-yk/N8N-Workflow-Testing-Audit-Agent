# N8N Workflow Testing & Audit Agent

A Telegram-controlled AI QA agent that audits n8n workflows, runs test scenarios, detects possible issues, and sends a structured workflow report back to Telegram.

This project was built to solve a practical problem: when an n8n workflow grows bigger, it becomes difficult to quickly understand what it does, whether it may break, where bugs may exist, and how it can be improved. This agent acts like a workflow testing assistant that can inspect an n8n workflow and return a clear quality report.

---

## Project Status

**Current version:** Working MVP / Version 1  
**Supported automatic execution:** n8n workflows with Webhook Trigger  
**Other workflow types:** Inspected and reported, but not automatically executed yet  
**Future goal:** Add broader trigger-node support and deeper workflow testing logic

---

## What This Agent Does

The agent is controlled through Telegram. A user can send a command such as:

```text
test <workflow name>
```

The system then:

1. Receives the workflow name from Telegram.
2. Connects to the n8n account using API access.
3. Loads and inspects the selected workflow.
4. Creates role-based QA test scenarios.
5. Runs supported workflow tests.
6. Captures browser/API evidence where possible.
7. Stores run details and reports in PostgreSQL.
8. Sends a structured QA report back to Telegram.

---

## Key Features

- **Telegram-based control** – Start workflow testing directly from Telegram.
- **n8n workflow inspection** – Reads workflow details and understands the workflow structure.
- **AI-assisted QA analysis** – Reviews workflow logic and identifies possible issues.
- **Four role-based test scenarios** – Simulates different user/business situations for testing.
- **Bug and risk detection** – Highlights failed scenarios, blocked flows, and weak points.
- **Improvement suggestions** – Gives practical recommendations to make workflows stronger.
- **PostgreSQL storage** – Stores workflow test runs, scenario results, and generated reports.
- **Model provider flexibility** – Supports Gemini, OpenAI, Anthropic, and Groq through configurable model providers.
- **Safe design** – Version 1 does not edit workflows automatically; it only inspects, tests, and reports.

---

## Architecture

```text
User
 ↓
Telegram Bot
 ↓
Main QA Agent
 ↓
n8n API + Browser Inspection
 ↓
Four Role-Based QA Scenarios
 ↓
Scenario Execution + Evidence Collection
 ↓
PostgreSQL Storage
 ↓
Structured QA Report
 ↓
Telegram Response
```

Detailed architecture is available in [`project-architecture.md`](project-architecture.md).

---

## Tech Stack

| Area | Tools / Technologies |
|---|---|
| Automation platform | n8n |
| Bot interface | Telegram Bot |
| Backend language | Python |
| Agent orchestration | LangGraph |
| Browser automation | Playwright |
| Database | PostgreSQL |
| AI model providers | Gemini, OpenAI, Anthropic, Groq |
| Config management | `.env` environment variables |
| Local setup | Docker Compose |
| Testing | Python test setup |

---

## Commands

```text
test <workflow name>
report latest
report <run_id>
```

Example:

```text
test Demo Lead QA Workflow
```

---

## Sample Output

The agent sends a report like this back to Telegram:

```text
QA Report: Demo Lead QA Workflow
Run ID: b7f3f3f0-9c2f-4d1f-8c7a-2b46c2a2f6e1

Passed: 3
Failed: 1
Blocked: 0

Failed Scenario:
- manager: invalid date format

Recommendation:
- Add clear validation for invalid date input.
```

Full sample output is available in [`sample-telegram-output.md`](sample-telegram-output.md).

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/shashank-yk/N8N-Workflow-Testing-Audit-Agent.git
cd N8N-Workflow-Testing-Audit-Agent
```

### 2. Create environment file

Copy the example environment file:

```bash
cp .env.example .env
```

Fill in the required values inside `.env`, such as:

```text
TELEGRAM_BOT_TOKEN=
N8N_BASE_URL=
N8N_API_KEY=
DATABASE_URL=
MODEL_PROVIDER=
```

### 3. Start PostgreSQL

```bash
docker compose up -d
```

### 4. Install Python dependencies

Use Python 3.11+.

```bash
pip install -e .[dev]
playwright install chromium
```

### 5. Create database tables

```bash
python -m qa_agent.db
```

### 6. Run the bot

```bash
python -m qa_agent.main
```

---

## Current Limitations

- Automatic execution currently works mainly for workflows with an n8n Webhook Trigger.
- Other trigger types are inspected and reported, but not fully auto-executed yet.
- The agent does not automatically edit or repair workflows in Version 1.
- Some advanced n8n node types may require custom testing logic in future versions.

These limitations are intentional for Version 1 because the project is designed to be safe, inspectable, and controlled before adding auto-fix capabilities.

---

## Future Improvements

Planned improvements include:

- Support for more n8n trigger nodes.
- Better scenario generation based on workflow type.
- Workflow risk scoring.
- Visual dashboard for test history.
- Auto-generated improvement checklist.
- Optional auto-fix suggestions with human approval.
- Better GitHub documentation with screenshots and demo video.

Full roadmap is available in [`future-improvements.md`](future-improvements.md).

---

## Portfolio Value

This project demonstrates practical experience with:

- AI agents
- n8n automation
- Telegram bot workflows
- API-based workflow inspection
- Multi-step QA automation
- Prompt engineering
- Agent orchestration
- Python backend development
- PostgreSQL storage
- Workflow testing and reporting

---

## Author

**Shashank Y K**  
GitHub: [shashank-yk](https://github.com/shashank-yk)

---

## License

This project is intended for learning, portfolio building, and practical AI automation experimentation.
