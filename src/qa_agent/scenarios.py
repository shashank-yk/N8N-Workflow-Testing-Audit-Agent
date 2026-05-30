from .models import Role, TestScenario


def build_role_scenarios() -> list[TestScenario]:
    return [
        TestScenario(
            role=Role.CUSTOMER,
            title="happy path with normal input",
            input_payload={"name": "Asha", "email": "asha@example.com", "phone": "9999999999"},
            expected_behavior="Workflow completes successfully for a valid customer submission.",
        ),
        TestScenario(
            role=Role.SALES,
            title="missing phone number",
            input_payload={"name": "Rahul", "email": "rahul@example.com", "phone": ""},
            expected_behavior="Workflow handles missing phone safely without crashing.",
        ),
        TestScenario(
            role=Role.MANAGER,
            title="invalid date format",
            input_payload={"date": "15-05-2026"},
            expected_behavior="Workflow rejects or normalizes invalid date input clearly.",
        ),
        TestScenario(
            role=Role.ADMIN,
            title="duplicate submission",
            input_payload={"name": "Asha", "email": "asha@example.com", "phone": "9999999999"},
            expected_behavior="Workflow handles duplicate data without unintended duplicate side effects.",
        ),
    ]
