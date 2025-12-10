import requests
import os

JIRA_URL = os.getenv("JIRA_URL")
JIRA_EMAIL = os.getenv("JIRA_EMAIL")
JIRA_API_TOKEN = os.getenv("JIRA_API_TOKEN")
PROJECT_KEY = os.getenv("PROJECT_KEY")

def create_jira_ticket(ticket: dict):
    url = f"{JIRA_URL}/rest/api/3/issue"
    auth = (JIRA_EMAIL, JIRA_API_TOKEN)

    payload = {
        "fields": {
            "project": {"key": PROJECT_KEY},
            "summary": ticket["title"],
            "description": ticket["description"],
            "issuetype": {"name": ticket["issue_type"]},
        }
    }

    response = requests.post(url, json=payload, auth=auth)
    return response.json()
