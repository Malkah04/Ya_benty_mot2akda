import uuid

from agents.generator.memory import (
    create_conversation,
    save_question,
    save_attempt,
    get_chat_history,
)
from ingestion.pipeline import ingest
from retrieval.retriever import retriever
from agents.generator.agent import generator_agent
from agents.evaluator.agent import evaluate_agent
from agents.evaluator.memory import save_evaluation
from storage.database import init_db
from agents.generator.agent_cache import save_semantic_response ,get_semantic_response

init_db()

def format_previous_attempts(attempts):
    if not attempts:
        return ""

    formatted = []

    for attempt in attempts:
        formatted.append(
            f"Attempt number: {attempt['attempt_number']}\n"
            f"Generated answer: {attempt['answer']}\n"
            f"Evaluator decision: {attempt['decision']}\n"
            f"Evaluator feedback: {attempt.get('feedback', '')}"
        )

    return "\n\n".join(formatted)


def process_source_question(
    source,
    source_type,
    question,
    conversation_id=None,
    max_attempts=4,
):
    if not question or not question.strip():
        raise ValueError("question cannot be empty")

    if not 1 <= max_attempts <= 4:
        raise ValueError("max_attempts must be between 1 and 4")

    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
        create_conversation(conversation_id)

    question_id = str(uuid.uuid4())

    cached_response = get_semantic_response(question,conversation_id=conversation_id)
    if cached_response is not None:
        print("LOGS: Returning cached response.\n")
        return {
            "conversation_id": conversation_id,
            "question_id": None,
            "answer": cached_response,
            "decision": "cached",
            "attempts_used": 0,
            "cached": True,
        }

    save_question(
        question_id=question_id,
        conversation_id=conversation_id,
        content=question,
    )
    print("LOGS: question saved in db \n")

    ingest(source, source_type)
    retriever_instance = retriever(k=3)
    context = retriever_instance.invoke(question)
    chat_history = get_chat_history(conversation_id)

    previous_attempts = []

    final_answer = None
    final_decision = None

    for attempt_number in range(1, max_attempts + 1):
        attempt_id = str(uuid.uuid4())

        attempts_text = format_previous_attempts(previous_attempts)

        generator_ans = generator_agent(
            context=context,
            question=question,
            chat_history=str(chat_history),
            previous_attempts=attempts_text,
        )
        print("LOGS: generator agent response \n")

        save_attempt(
            attempt_id=attempt_id,
            question_id=question_id,
            attempt_number=attempt_number,
            answer=generator_ans,
        )
        print("LOGS: generator answer saved in db \n")


        evaluation = evaluate_agent(
            question=question,
            context=context,
            answer=generator_ans,
        )
        print("LOGS: evaluation model response \n")
        print("Evaluation type:", type(evaluation))
        print("Evaluation value:", repr(evaluation))
        print(evaluation)

        decision = evaluation["decision"]
        if decision not in ("accept", "revise"):
            raise ValueError(
                f"Unexpected evaluator decision: {decision}"
            )

        save_evaluation(
            evaluation_id=str(uuid.uuid4()),
            attempt_id=attempt_id,
            decision=decision,
            feedback=evaluation.get("feedback", ""),
            accuracy=evaluation.get("accuracy"),
            relevance=evaluation.get("relevance"),
            completeness=evaluation.get("completeness"),
            consistency=evaluation.get("consistency"),
            grounding=evaluation.get("grounding"),
            unsupported_claims=evaluation.get("unsupported_claims"),
            overall_quality=evaluation.get("overall_quality"),
        )
        print("LOGS : evaluation answer saved in db \n")

        previous_attempts.append({
            "attempt_number": attempt_number,
            "answer": generator_ans,
            "decision": decision,
            "feedback": evaluation.get("feedback", ""),
        })

        final_answer = generator_ans
        final_decision = decision

        if decision == "accept":
            save_semantic_response(question,generator_ans ,conversation_id)
            print("LOGS : decision of evaluation is accepted and saved in cache \n")
            break

    return {
        "conversation_id": conversation_id,
        "question_id": question_id,
        "answer": final_answer,
        "decision": final_decision,
        "attempts_used": len(previous_attempts),
    }


# res= process_source_question("Malak_Sobhy_CV.pdf" ,"file","what is malak skills?")
# print("workflow result:",res)