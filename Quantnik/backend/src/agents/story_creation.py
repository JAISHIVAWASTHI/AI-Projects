def create_team_managed_project():
    url = f"{JIRA_BASE}/rest/api/3/project"

    payload = {
        "key": "AISCR",  # must be unique
        "name": "AI Scoring Engine Project",
        "projectTypeKey": "software",
        "projectTemplateKey": "com.pyxis.greenhopper.jira:gh-scrum-team-managed",
        "assigneeType": "UNASSIGNED",
        "leadAccountId": None,
    }
