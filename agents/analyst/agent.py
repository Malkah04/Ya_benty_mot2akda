from agents.llm import llm
from agents.analyst.tools import tools
from langchain.agents import create_agent
from agents.analyst.prompt import ANALYST_SYSTEM_PROMPT
from pydantic import BaseModel
from typing import Literal

class AnalystResponse(BaseModel):
    status: Literal["complete", "need_more_evidence"]
    answer: str | None = None
    query: str | None = None

ana_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt=ANALYST_SYSTEM_PROMPT,
    response_format=AnalystResponse
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

    return response["structured_response"].model_dump()