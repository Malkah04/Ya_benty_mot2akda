from agents.llm import llm
from agents.analyst.tools import tools
from langchain.agents import create_agent
from agents.analyst.prompt import ANALYST_SYSTEM_PROMPT
import json

ana_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=ANALYST_SYSTEM_PROMPT
)

def analyze_evidence(question: str, evidence: list, chat_history: str):

    response = ana_agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"""
            CONVERSATION HISTORY:
            {chat_history}

            CURRENT USER QUESTION:
            {question}

            RETRIEVED EVIDENCE:
            {evidence}
            """
        }]
    })

    for i, message in enumerate(response["messages"]):
        print(f"\n--- Message {i} ---")
        print("Type:", type(message).__name__)

        if hasattr(message, "tool_calls") and message.tool_calls:
            for tool_call in message.tool_calls:
                print("Tool name:", tool_call["name"])
                print("Tool arguments:", tool_call["args"])
                print("Tool call ID:", tool_call["id"])

        elif message.type == "tool":
            print("Executed tool:", message.name)
            print("Tool result:", message.content)

    return json.loads(response["messages"][-1].content)
