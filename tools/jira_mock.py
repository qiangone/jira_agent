"""
Mock Jira Client -- Simulates Jira locally for testing without a real Atlassian account.
Enable by setting JIRA_MOCK=true in your .env file.
"""

from datetime import datetime

BASE_URL = "https://mock.atlassian.net"

# ── Mock data store ───────────────────────────────────────────
_issues: dict = {
    "DEV-1": {
        "key": "DEV-1",
        "summary": "Login page 500 error",
        "description": "Users report intermittent 500 errors on login. Needs investigation in auth service.",
        "status": "In Progress", "assignee": "Alice", "reporter": "Bob",
        "priority": "High", "type": "Bug",
        "created": "2024-01-10T09:00:00", "updated": "2024-01-15T14:30:00",
    },
    "DEV-2": {
        "key": "DEV-2",
        "summary": "Refactor payment module",
        "description": "Migrate legacy payment module to new architecture.",
        "status": "To Do", "assignee": "Charlie", "reporter": "Alice",
        "priority": "Medium", "type": "Story",
        "created": "2024-01-12T10:00:00", "updated": "2024-01-12T10:00:00",
    },
    "DEV-3": {
        "key": "DEV-3",
        "summary": "Optimize homepage load time",
        "description": "Homepage LCP exceeds 3s. Optimize images and API calls.",
        "status": "Done", "assignee": "Diana", "reporter": "Charlie",
        "priority": "Low", "type": "Task",
        "created": "2024-01-08T08:00:00", "updated": "2024-01-14T16:00:00",
    },
    "DEV-4": {
        "key": "DEV-4",
        "summary": "Add user export feature",
        "description": "Admin panel should support exporting user list as Excel.",
        "status": "In Progress", "assignee": "Alice", "reporter": "Bob",
        "priority": "Medium", "type": "Task",
        "created": "2024-01-13T11:00:00", "updated": "2024-01-16T09:00:00",
    },
    "DEV-5": {
        "key": "DEV-5",
        "summary": "iOS app crash on notification tap",
        "description": "App crashes on iOS 16 when tapping push notifications.",
        "status": "To Do", "assignee": "Unassigned", "reporter": "Diana",
        "priority": "Highest", "type": "Bug",
        "created": "2024-01-16T15:00:00", "updated": "2024-01-16T15:00:00",
    },
}

_next_id: dict = {"DEV": 6}

VALID_TRANSITIONS = ["To Do", "In Progress", "In Review", "Done"]


def _make_url(key: str) -> str:
    return f"{BASE_URL}/browse/{key}"


def _next_key(project_key: str) -> str:
    n = _next_id.get(project_key, 1)
    _next_id[project_key] = n + 1
    return f"{project_key}-{n}"


def _match_jql(issue: dict, jql: str) -> bool:
    """Simple JQL matching: supports project, status, issuetype, assignee, priority, text."""
    jql_lower = jql.lower()

    if "project=" in jql_lower:
        val = jql_lower.split("project=")[1].split()[0].strip('"\'')
        if not issue["key"].lower().startswith(val):
            return False

    for part in jql_lower.split("and"):
        part = part.strip()
        if "status" in part and "=" in part:
            val = part.split("=")[1].strip().strip('"\'')
            if issue["status"].lower() != val:
                return False

    if "issuetype=" in jql_lower:
        val = jql_lower.split("issuetype=")[1].split()[0].strip('"\'')
        if issue["type"].lower() != val:
            return False

    if "assignee=" in jql_lower:
        val = jql_lower.split("assignee=")[1].split()[0].strip('"\'')
        if val != "currentuser()" and issue["assignee"].lower() != val:
            return False

    if "priority=" in jql_lower:
        val = jql_lower.split("priority=")[1].split()[0].strip('"\'')
        if issue["priority"].lower() != val:
            return False

    if "text~" in jql_lower:
        val = jql_lower.split("text~")[1].split()[0].strip('"\'')
        if val not in issue["summary"].lower() and val not in issue["description"].lower():
            return False

    return True


# ── Mock Client (same interface as JiraClient) ────────────────
class JiraMockClient:

    def search_issues(self, jql: str, max_results: int = 10):
        results = [
            {
                "key":      i["key"],
                "summary":  i["summary"],
                "status":   i["status"],
                "assignee": i["assignee"],
                "priority": i["priority"],
                "type":     i["type"],
                "url":      _make_url(i["key"]),
            }
            for i in _issues.values()
            if _match_jql(i, jql)
        ]
        return results[:max_results]

    def get_issue(self, issue_key: str):
        issue = _issues.get(issue_key.upper())
        if not issue:
            raise ValueError(f"Issue {issue_key} not found in mock data")
        return {**issue, "url": _make_url(issue["key"])}

    def create_issue(self, project_key: str, summary: str, description: str,
                     issue_type: str = "Task", priority: str = "Medium"):
        key = _next_key(project_key.upper())
        _issues[key] = {
            "key": key, "summary": summary, "description": description,
            "status": "To Do", "assignee": "Unassigned", "reporter": "Current User",
            "priority": priority, "type": issue_type,
            "created": datetime.now().isoformat(),
            "updated": datetime.now().isoformat(),
        }
        return {"key": key, "url": _make_url(key)}

    def transition_issue(self, issue_key: str, transition_name: str):
        issue = _issues.get(issue_key.upper())
        if not issue:
            raise ValueError(f"Issue {issue_key} not found")
        matched = next(
            (t for t in VALID_TRANSITIONS if t.lower() == transition_name.lower()), None
        )
        if not matched:
            raise ValueError(f"Transition '{transition_name}' not found. Available: {VALID_TRANSITIONS}")
        _issues[issue_key.upper()]["status"] = matched
        _issues[issue_key.upper()]["updated"] = datetime.now().isoformat()
        return {"key": issue_key, "new_status": matched}

    def add_comment(self, issue_key: str, comment: str):
        if issue_key.upper() not in _issues:
            raise ValueError(f"Issue {issue_key} not found")
        return {"key": issue_key, "status": "comment added", "comment": comment}

    def update_issue(self, issue_key: str, summary: str = None, priority: str = None):
        issue = _issues.get(issue_key.upper())
        if not issue:
            raise ValueError(f"Issue {issue_key} not found")
        if not summary and not priority:
            raise ValueError("At least one of 'summary' or 'priority' must be provided")
        updated = []
        if summary:
            _issues[issue_key.upper()]["summary"] = summary
            updated.append("summary")
        if priority:
            _issues[issue_key.upper()]["priority"] = priority
            updated.append("priority")
        _issues[issue_key.upper()]["updated"] = datetime.now().isoformat()
        return {"key": issue_key, "updated_fields": updated}
