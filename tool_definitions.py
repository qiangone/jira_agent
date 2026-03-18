TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "jira_search_issues",
            "description": "Search Jira issues using JQL, e.g. 'project=DEV AND status=Open'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "jql": {
                        "type": "string",
                        "description": "JQL query string, e.g. 'project=DEV AND issuetype=Bug AND status=\"In Progress\"'",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return. Default is 10.",
                    },
                },
                "required": ["jql"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "jira_get_issue",
            "description": "Get detailed information about a single Jira issue including status, assignee, and priority.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key, e.g. DEV-42",
                    },
                },
                "required": ["issue_key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "jira_create_issue",
            "description": "Create a new Jira issue such as a Task, Bug, or Story.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "The project key, e.g. DEV",
                    },
                    "summary": {
                        "type": "string",
                        "description": "The issue title/summary",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the issue",
                    },
                    "issue_type": {
                        "type": "string",
                        "description": "Issue type: Task, Bug, or Story. Default is Task.",
                    },
                    "priority": {
                        "type": "string",
                        "description": "Priority: Highest, High, Medium, or Low. Default is Medium.",
                    },
                },
                "required": ["project_key", "summary", "description"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "jira_create_subtask",
            "description": "Create a subtask under an existing Jira issue (parent).",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "The project key, e.g. DEV",
                    },
                    "parent_key": {
                        "type": "string",
                        "description": "The parent issue key, e.g. DEV-42",
                    },
                    "summary": {
                        "type": "string",
                        "description": "The subtask title/summary",
                    },
                    "description": {
                        "type": "string",
                        "description": "Detailed description of the subtask (optional)",
                    },
                },
                "required": ["project_key", "parent_key", "summary"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "jira_transition_issue",
            "description": "Transition a Jira issue to a new status, e.g. 'In Progress' or 'Done'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key, e.g. DEV-42",
                    },
                    "transition_name": {
                        "type": "string",
                        "description": "Target status name, e.g. In Progress, Done, To Do",
                    },
                },
                "required": ["issue_key", "transition_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "jira_add_comment",
            "description": "Add a comment to a Jira issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key, e.g. DEV-42",
                    },
                    "comment": {
                        "type": "string",
                        "description": "The comment text to add",
                    },
                },
                "required": ["issue_key", "comment"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "jira_update_issue",
            "description": "Update the summary or priority of a Jira issue.",
            "parameters": {
                "type": "object",
                "properties": {
                    "issue_key": {
                        "type": "string",
                        "description": "The issue key, e.g. DEV-42",
                    },
                    "summary": {
                        "type": "string",
                        "description": "New summary/title (optional)",
                    },
                    "priority": {
                        "type": "string",
                        "description": "New priority: Highest, High, Medium, or Low (optional)",
                    },
                },
                "required": ["issue_key"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "jira_get_subtasks",
            "description": "Get all subtasks under a parent issue, optionally filtered by summary keyword.",
            "parameters": {
                "type": "object",
                "properties": {
                    "parent_key": {
                        "type": "string",
                        "description": "The parent issue key, e.g. AGENT-1",
                    },
                    "summary_filter": {
                        "type": "string",
                        "description": "Keyword to filter subtasks by summary (optional)",
                    },
                },
                "required": ["parent_key"],
            },
        },
    },
    
]
