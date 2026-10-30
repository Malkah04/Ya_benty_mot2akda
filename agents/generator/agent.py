from agents.llm import llm
from agents.generator.prompt import prompt
from agents.generator.agent_cache import get_semantic_response, save_semantic_response

generator_chain = prompt | llm

def format_context(context):
    if isinstance(context, str):
        return context.strip()
    
    formatted_docs = []
    for doc in context:
        source = doc.metadata.get("source", "Unknown source")
        formatted_docs.append(
            f"Source: {source}\n{doc.page_content}"
        )

    return "\n\n".join(formatted_docs)




def generator_agent(context ,question,chat_history ="" ,previous_attempts=""):
    if not question.strip():
        raise ValueError("question can't be empty")

    inputs = {
        "question": question,
        "context": format_context(context),
        "chat_history": chat_history,
        "previous_attempts": previous_attempts,
    }
    response = generator_chain.invoke(inputs)
    print("Generator response:", response.content)
    return response.content

    