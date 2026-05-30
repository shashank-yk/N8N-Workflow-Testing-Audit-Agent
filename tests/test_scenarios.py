from qa_agent.models import Role
from qa_agent.scenarios import build_role_scenarios


def test_build_role_scenarios_has_all_roles():
    scenarios = build_role_scenarios()
    assert {scenario.role for scenario in scenarios} == {
        Role.CUSTOMER,
        Role.SALES,
        Role.MANAGER,
        Role.ADMIN,
    }
