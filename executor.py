import json
import os
from dotenv import load_dotenv
import requests
from tools.cr_workflow import create_component_cr as _create_component_cr, create_db_cr as _create_db_cr

load_dotenv()

if os.getenv("JIRA_MOCK", "false").lower() == "true":
    from tools.jira_mock import JiraMockClient as JiraClient
    print("[Mock mode enabled] Using local mock data. No real Jira requests will be made.")
else:
    from tools.jira import JiraClient

jira = JiraClient()

TOOL_MAP = {
    "jira_search_issues":    lambda p: jira.search_issues(**p),
    "jira_get_issue":        lambda p: jira.get_issue(**p),
    "jira_create_issue":     lambda p: jira.create_issue(**p),
    "jira_create_subtask":   lambda p: jira.create_subtask(**p),
    "jira_transition_issue": lambda p: jira.transition_issue(**p),
    "jira_add_comment":      lambda p: jira.add_comment(**p),
    "jira_update_issue":     lambda p: jira.update_issue(**p),
    "jira_get_subtasks":     lambda p: jira.get_subtasks(**p),
    "create_component_cr":  lambda p: _create_component_cr(**p),
    "create_db_cr":         lambda p: _create_db_cr(**p),
}


# def execute_tool(tool_name: str, tool_input: dict) -> str:
#     if tool_name not in TOOL_MAP:
#         return json.dumps({"error": f"Unknown tool: {tool_name}"}, ensure_ascii=False)
#     try:
#         result = TOOL_MAP[tool_name](tool_input)
#         return json.dumps(result, ensure_ascii=False, indent=2)
#     except Exception as e:
#         return json.dumps({"error": str(e)}, ensure_ascii=False)

def execute_tool(tool_name: str, tool_input: dict) -> str:
    if tool_name not in TOOL_MAP:
        return json.dumps({"error": f"Unknown tool: {tool_name}"})
    try:
        result = TOOL_MAP[tool_name](tool_input)
        return json.dumps(result, ensure_ascii=False, indent=2)
    except requests.exceptions.HTTPError as e:
        # Parse Jira's error response for a cleaner message
        try:
            print(e)
            detail = e.response.json()
            messages = detail.get("errorMessages", [])
            errors = detail.get("errors", {})
            msg = "; ".join(messages) if messages else str(errors) if errors else str(e)
        except Exception:
            msg = str(e)
        return json.dumps({"error": msg})
    except Exception as e:
        print(e)
        return json.dumps({"error": str(e)})