import json

from agents.evaluator.prompt import prompt
from agents.llm import llm

evaluator_chain = prompt | llm

def evaluate_agent(question , context ,answer):
    if not question or not context or not answer:
        raise ValueError("all argument required")

    input ={
        "question":question,
        "context":context ,
        "answer":answer
    }
    response =evaluator_chain.invoke(input)
    print("LOGS : evaluator agent response generated \n")
    return json.loads(response.content)