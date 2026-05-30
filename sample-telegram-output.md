# Sample Telegram Output

This is an example of the kind of report the bot sends after a user runs:

```text
test Demo Lead QA Workflow
```

Example response:

```markdown
# QA Report: Demo Lead QA Workflow
Run ID: `b7f3f3f0-9c2f-4d1f-8c7a-2b46c2a2f6e1`
Created: 2026-05-30T12:15:00.000000

Passed: 3
Failed: 1
Blocked: 0

## Passed scenarios
- customer: happy path with normal input
- sales: missing phone number
- admin: duplicate submission

## Failed scenarios
- manager: invalid date format - Webhook returned HTTP 400; inspect branch handling for invalid date format.

## Blocked scenarios
- None

## Recommendations
- Add clear validation for invalid date input.
```

If a workflow does not use a supported trigger type, the report marks scenarios as blocked instead of claiming they were fully tested.
