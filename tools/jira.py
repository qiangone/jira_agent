import requests
from config import ATLASSIAN_URL, ATLASSIAN_TOKEN


class JiraClient:
    def __init__(self):
        self.base    = f"{ATLASSIAN_URL}/rest/api/2"
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {ATLASSIAN_TOKEN}"
        }

    def _req(self, method, endpoint, **kwargs):
        r = requests.request(
            method, f"{self.base}/{endpoint}",
            headers=self.headers, **kwargs
        )
        r.raise_for_status()
        return r.json() if r.content else {}

    def search_issues(self, jql: str, max_results: int = 10):
        jql = self._fix_jql(jql)
        data = self._req("GET", "search", params={
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,priority,issuetype",
        })
        return [
            {
                "key":      i["key"],
                "summary":  i["fields"]["summary"],
                "status":   i["fields"]["status"]["name"],
                "assignee": (i["fields"].get("assignee") or {}).get("displayName", "Unassigned"),
                "priority": (i["fields"].get("priority") or {}).get("name", "-"),
                "type":     i["fields"]["issuetype"]["name"],
                "url":      f"{ATLASSIAN_URL}/browse/{i['key']}",
            }
            for i in data.get("issues", [])
        ]

    def get_issue(self, issue_key: str):
        data = self._req("GET", f"issue/{issue_key}")
        f = data["fields"]
        return {
            "key":         data["key"],
            "summary":     f["summary"],
            "status":      f["status"]["name"],
            "assignee":    (f.get("assignee") or {}).get("displayName", "Unassigned"),
            "reporter":    (f.get("reporter") or {}).get("displayName", "-"),
            "priority":    (f.get("priority") or {}).get("name", "-"),
            "type":        f["issuetype"]["name"],
            "created":     f["created"],
            "updated":     f["updated"],
            "url":         f"{ATLASSIAN_URL}/browse/{data['key']}",
        }

    def create_issue(self, project_key: str, summary: str, description: str,
                     issue_type: str = "Task", priority: str = "Medium"):
        payload = {"fields": {
            "project":     {"key": project_key},
            "summary":     summary,
            "issuetype":   {"name": issue_type},
            "priority":    {"name": priority},
            "description": description,
        }}
        data = self._req("POST", "issue", json=payload)
        return {"key": data["key"], "url": f"{ATLASSIAN_URL}/browse/{data['key']}"}

    def transition_issue(self, issue_key: str, transition_name: str):
        transitions = self._req("GET", f"issue/{issue_key}/transitions")
        target = next(
            (t for t in transitions["transitions"]
             if t["name"].lower() == transition_name.lower()), None
        )
        if not target:
            available = [t["name"] for t in transitions["transitions"]]
            raise ValueError(f"Transition '{transition_name}' not found. Available: {available}")
        self._req("POST", f"issue/{issue_key}/transitions",
                  json={"transition": {"id": target["id"]}})
        return {"key": issue_key, "new_status": transition_name}

    def add_comment(self, issue_key: str, comment: str):
        payload = {"body": comment}
        self._req("POST", f"issue/{issue_key}/comment", json=payload)
        return {"key": issue_key, "status": "comment added"}

    def update_issue(self, issue_key: str, summary: str = None, priority: str = None):
        fields = {}
        if summary:
            fields["summary"] = summary
        if priority:
            fields["priority"] = {"name": priority}
        if not fields:
            raise ValueError("At least one of 'summary' or 'priority' must be provided")
        self._req("PUT", f"issue/{issue_key}", json={"fields": fields})
        return {"key": issue_key, "updated_fields": list(fields.keys())}

    def create_subtask(self, project_key: str, parent_key: str,
                   summary: str, description: str = ""):
        payload = {"fields": {
            "project":     {"key": project_key},
            "parent":      {"key": parent_key},
            "summary":     summary,
            "issuetype":   {"name": "Sub-task"},
            "description": description,
        }}
        data = self._req("POST", "issue", json=payload)
        return {"key": data["key"], "url": f"{ATLASSIAN_URL}/browse/{data['key']}"}

    def get_subtasks(self, parent_key: str, summary_filter: str = None):
        jql = f'parent="{parent_key}" AND issuetype="Sub-task"'
        if summary_filter:
            jql += f' AND summary~"{summary_filter}"'
        data = self._req("GET", "search", params={
            "jql": jql,
            "maxResults": 50,
            "fields": "summary,status,assignee,priority",
        })
        return [
            {
                "key":      i["key"],
                "summary":  i["fields"]["summary"],
                "status":   i["fields"]["status"]["name"],
                "assignee": (i["fields"].get("assignee") or {}).get("displayName", "Unassigned"),
                "priority": (i["fields"].get("priority") or {}).get("name", "-"),
                "url":      f"{ATLASSIAN_URL}/browse/{i['key']}",
            }
            for i in data.get("issues", [])
        ]

    def _fix_jql(self, jql: str) -> str:
        """Normalize quotes and status names in JQL to handle common variations."""
        import re

        # Mapping of common status variations to standard forms
        # Add more mappings as needed for your Jira instance
        status_mapping = {
            "to do": "To Do",
            "todo": "To Do",
            "to-do": "To Do",
            "in progress": "In Progress",
            "inprogress": "In Progress",
            "in-progress": "In Progress",
            "done": "Done",
            "backlog": "Backlog",
            "open": "Open",
            "new": "New",
            "in review": "In Review",
            "in-review": "In Review",
        }

        # First, convert single quotes to double quotes
        jql = re.sub(r"status\s*=\s*'([^']+)'", r'status = "\1"', jql)

        # Then, normalize status values to try common variations
        def normalize_status(match):
            prefix = match.group(1)  # e.g., 'status = '
            status_value = match.group(2)  # e.g., 'To Do'

            # Try exact match first
            if status_value in status_mapping:
                return f'{prefix}"{status_mapping[status_value]}"'

            # Try case-insensitive match
            lower_status = status_value.lower()
            for key, mapped_value in status_mapping.items():
                if key == lower_status:
                    return f'{prefix}"{mapped_value}"'

            # If no mapping found, keep original
            return f'{prefix}"{status_value}"'

        # Replace status values with normalized ones
        jql = re.sub(r'(status\s*=\s*)"([^"]+)"', normalize_status, jql)

        return jql
