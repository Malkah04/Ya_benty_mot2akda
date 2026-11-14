from agents.llm import llm
from agents.retriever.tools import tools
from langchain.agents import create_agent
from agents.retriever.prompt import RETRIEVER_SYSTEM_PROMPT

llm.bind_tools(tools)

retriever_agent =create_agent(
    model=llm,
    tools=tools,
    system_prompt= RETRIEVER_SYSTEM_PROMPT
)


def retrieve_evidence(query, chat_history):
    """
    Invoke Retriever Agent with query and conversation history.
    """

    response = retriever_agent.invoke({
        "messages": [{
            "role": "user",
            "content": f"""
            Previous conversation:
            {chat_history}

            Current question:
            {query}
            """
        }]
    })

    return response

