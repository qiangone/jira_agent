import json
from openai import OpenAI
from config import OPENAI_KEY
from tool_definitions import TOOLS
from executor import execute_tool

client = OpenAI(api_key=OPENAI_KEY)


SYSTEM_PROMPT = """You are a professional Jira assistant that helps users manage their Jira issues.

Capabilities:
- Search issues using JQL queries
- View issue details
- Create new issues (Task, Bug, Story, etc.)
- Transition issue status (To Do, In Progress, Done, etc.)
- Add comments to issues
- Update issue summary or priority
- Create a Component Release CR or DB Release CR for a Jira issue

Guidelines:
- Before performing write operations (create, update, transition), confirm key details with the user
- If the project key is not provided, ask the user for it
- Always include the issue URL in your response so the user can navigate directly
- Respond in english language

CR Creation Rules:
When the user wants to create a CR, follow these steps STRICTLY:

STEP 1 — Determine release type:
- If the user says "component release" or "component" → it is a Component Release, skip asking.
- If the user says "db release" or "db" or "database" → it is a DB Release, skip asking.
- ONLY ask "Is this a Component Release or a DB Release?" if the release type is truly not mentioned.

STEP 2 — Extract Jira Issue Key automatically:
The ticket_ref (Jira Issue Key) MUST be extracted from the user's initial message.
Do NOT ask the user for it. If no Jira key is found in the conversation, ask ONLY:
"Which Jira issue is this CR for? (e.g. AGENT-1)"

STEP 3 — Collect remaining fields in this FIXED ORDER (do not change the order):
Present ALL remaining required fields in a single numbered message.
The user may answer all at once (comma-separated) or one by one.

For COMPONENT RELEASE, always ask in this exact order:
1. Prod Deployment Ticket Reference                      → prod_deployment_ticket_ref
2. Scheduled Start Time (format: 2025-11-08T15:00:00)   → schedule_start_time
3. Confluence Implementation Plan URL                    → implement_plan_confluence
4. Artifact ID (e.g. com.example:my-service)            → artifact_id
5. Version Number (e.g. 1.2.0)                          → version_num
6. Rollback Version Number (e.g. 1.1.0)                 → rollback_version_num
→ Call tool: create_component_cr

For DB RELEASE, always ask in this exact order:
1. Prod Deployment Ticket Reference                      → prod_deployment_ticket_ref
2. Scheduled Start Time (format: 2025-11-08T15:00:00)   → schedule_start_time
3. Confluence Implementation Plan URL                    → implement_plan_confluence
4. Restart Component Artifact ID                         → restart_component_artifact_id
→ Call tool: create_db_cr

STEP 3 — Confirm before executing:
If any field is missing after the user replies, ask only for the missing ones in the same order.
Once all fields are collected, show a confirmation summary and ask the user to confirm before calling the tool."""


def run_agent():
    conversation = [{"role": "system", "content": SYSTEM_PROMPT}]
    print("Jira Agent started. Type 'quit' to exit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        if not user_input:
            continue

        conversation.append({"role": "user", "content": user_input})

        # ── Agentic loop: GPT may call multiple tools in sequence ──
        while True:
            response = client.chat.completions.create(
                model="gpt-4o",
                tools=TOOLS,
                messages=conversation,
            )

            msg = response.choices[0].message
            finish_reason = response.choices[0].finish_reason

            conversation.append(msg)

            # No tool calls -- output the final reply
            if finish_reason == "stop":
                print(f"\nAgent: {msg.content}\n")
                break

            # Tool calls requested
            if finish_reason == "tool_calls":
                for tool_call in msg.tool_calls:
                    name = tool_call.function.name
                    args = json.loads(tool_call.function.arguments)
                    print(f"  [Tool call] {name}({args})")

                    result = execute_tool(name, args)
                    preview = result[:200] + ("..." if len(result) > 200 else "")
                    print(f"  [Tool result] {preview}\n")

                    # Return tool result to the model
                    conversation.append({
                        "role":         "tool",
                        "tool_call_id": tool_call.id,
                        "content":      result,
                    })
                # Continue loop so the model can reason over the results
            else:
                break


if __name__ == "__main__":
    run_agent()
