# Sample Telegram Output

This is an example of the type of report the bot sends after a user runs:

```text
test Demo Lead QA Workflow
```

---

## Example Response

```text
# QA Report: Demo Lead QA Workflow

Run ID: b7f3f3f0-9c2f-4d1f-8c7a-2b46c2a2f6e1
Created: 2026-05-30T12:15:00.000000

## Summary
Passed: 3
Failed: 1
Blocked: 0

## Workflow Understanding
This workflow appears to collect lead information, validate user details, and send the lead data to the next business process.

## Passed Scenarios
- customer: happy path with normal input
- sales: missing phone number handled correctly
- admin: duplicate submission detected

## Failed Scenarios
- manager: invalid date format
  Reason: Webhook returned HTTP 400.
  Suggested action: Inspect branch handling for invalid date format.

## Blocked Scenarios
- None

## Recommendations
- Add clear validation for invalid date input.
- Add fallback error response for failed webhook calls.
- Add logging for failed executions.
- Add a human-readable error message for users.
```

---

## Unsupported Trigger Example

If a workflow does not use a currently supported trigger type, the report should clearly say that the workflow was inspected but not fully executed.

```text
# QA Report: Google Sheets Lead Workflow

Status: Inspection completed
Automatic execution: Blocked
Reason: Current version supports automatic execution mainly for Webhook Trigger workflows.

## What was inspected
- Workflow structure
- Node connections
- Possible failure points
- Missing error-handling paths

## Recommendation
Add a test webhook wrapper or extend the agent to support Google Sheets Trigger execution.
```

This avoids falsely claiming that the workflow was fully tested.
