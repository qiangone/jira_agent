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
- Create sub task
- Transition issue status (To Do, In Progress, Done, etc.)
- Add comments to issues
- Update issue summary or priority

Guidelines:
- Before performing write operations (create, update, transition), confirm key details with the user
- If the project key is not provided, ask the user for it
- Always include the issue URL in your response so the user can navigate directly
- Respond in the same language the user is using"""


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
