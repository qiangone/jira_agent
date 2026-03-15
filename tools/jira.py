import requests
from requests.auth import HTTPBasicAuth
from config import ATLASSIAN_URL, ATLASSIAN_EMAIL, ATLASSIAN_TOKEN


class JiraClient:
    def __init__(self):
        self.base    = f"{ATLASSIAN_URL}/rest/api/3"
        self.auth    = HTTPBasicAuth(ATLASSIAN_EMAIL, ATLASSIAN_TOKEN)
        self.headers = {"Accept": "application/json", "Content-Type": "application/json"}

    def _req(self, method, endpoint, **kwargs):
        r = requests.request(
            method, f"{self.base}/{endpoint}",
            auth=self.auth, headers=self.headers, **kwargs
        )
        r.raise_for_status()
        return r.json() if r.content else {}

    def search_issues(self, jql: str, max_results: int = 10):
        data = self._req("POST", "issue/search", json={
            "jql": jql,
            "maxResults": max_results,
            "fields": ["summary", "status", "assignee", "priority", "issuetype"],
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
            "description": {
                "type": "doc", "version": 1,
                "content": [{"type": "paragraph",
                             "content": [{"type": "text", "text": description}]}],
            },
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
        payload = {"body": {
            "type": "doc", "version": 1,
            "content": [{"type": "paragraph",
                         "content": [{"type": "text", "text": comment}]}],
        }}
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
