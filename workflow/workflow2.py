import uuid
from ingestion.pipeline import ingest
from agents.generator.memory import create_conversation,save_question,get_chat_history
from agents.generator.agent_cache import save_semantic_response,get_semantic_response
from storage.database import init_db
from agents.analyst.agent import analyze_evidence
from agents.retriever.agent import retrieve_evidence

init_db()

MAX_RETRIEVAL_ROUNDS = 3

def normalize_evidence(result):
    """
    Ensure Retriever Agent returns a list of evidence dictionaries.
    Each item must contain content and metadata.
    """

    if isinstance(result, list):
        return result

    if isinstance(result, dict):
        return result.get("evidence", [])

    raise ValueError("Unexpected Retriever Agent output.")


def merge_evidence(old_evidence, new_evidence):
    """
    Merge retrieved evidence without adding duplicate chunks.
    """

    existing_ids = {
        (
            item.get("metadata", {}).get("chunk_id")
            or item.get("content", "")
        )
        for item in old_evidence
    }

    for item in new_evidence:
        item_id = (
            item.get("metadata", {}).get("chunk_id")
            or item.get("content", "")
        )

        if item_id not in existing_ids:
            old_evidence.append(item)
            existing_ids.add(item_id)

    return old_evidence


def process_source_question(source,source_type,question,conversation_id=None, max_retrieval_rounds=MAX_RETRIEVAL_ROUNDS,):

    if not question or not question.strip():
        raise ValueError("Question cannot be empty.")

    if not 0 <= max_retrieval_rounds <= 5:
        raise ValueError(
            "max_retrieval_rounds must be between 0 and 5."
        )

    if conversation_id is None:
        conversation_id = str(uuid.uuid4())
        create_conversation(conversation_id)

    question_id = str(uuid.uuid4())

    cached_response = get_semantic_response(
        question,
        conversation_id=conversation_id
    )

    if cached_response is not None:
        print("LOGS: Returning cached response.")

        return {
            "conversation_id": conversation_id,
            "question_id": None,
            "answer": cached_response,
            "status": "cached",
            "retrieval_rounds": 0,
            "cached": True,
        }

    save_question(
        question_id=question_id,
        conversation_id=conversation_id,
        content=question,
    )

    if isinstance(source, list):
        for file_path in source:
            ingest(file_path, source_type)
    else:
        ingest(source, source_type)

    chat_history = get_chat_history(conversation_id)

    print("LOGS: Starting initial retrieval.")

    evidence = (retrieve_evidence(question ,chat_history))
    print("LOGS: got evidence from retrievel agent" , evidence)

    if not evidence:
        return {
            "conversation_id": conversation_id,
            "question_id": question_id,
            "answer": "No relevant evidence was found.",
            "status": "no_evidence",
            "retrieval_rounds": 0,
            "cached": False,
        }

    retrieval_rounds = 0

    while True:

        print("LOGS: Analyst is analyzing evidence.")

        analysis = analyze_evidence(
            question=question,
            evidence=evidence,
            chat_history=chat_history
        )
        print("LOGS: analyst agent res" ,analysis)

        status = analysis.get("status")

        if status == "complete":
            final_answer = analysis.get("answer", "")

            save_semantic_response(
                question,
                final_answer,
                conversation_id
            )
            print("LOGS: Analysis completed.")

            return {
                "conversation_id": conversation_id,
                "question_id": question_id,
                "answer": final_answer,
                "status": "complete",
                "retrieval_rounds": retrieval_rounds,
                "evidence_count": len(evidence),
                "cached": False,
            }

        elif status == "need_more_evidence":

            if retrieval_rounds >= max_retrieval_rounds:

                print("LOGS: Maximum retrieval rounds reached.")

                return {
                    "conversation_id": conversation_id,
                    "question_id": question_id,
                    "answer": analysis.get(
                        "answer",
                        "The available evidence is insufficient "
                        "to provide a reliable answer."
                    ),
                    "status": "insufficient_evidence",
                    "retrieval_rounds": retrieval_rounds,
                    "evidence_count": len(evidence),
                    "cached": False,
                }

            new_query = analysis.get("query")

            if not new_query or not new_query.strip():
                raise ValueError(
                    "Analyst requested more evidence without a query."
                )

            print(
                f"LOGS: Retrieving additional evidence: {new_query}"
            )

            new_evidence = (retrieve_evidence(new_query ,chat_history))

            retrieval_rounds += 1

            if not new_evidence:
                print("LOGS: No additional evidence found.")

                return {
                    "conversation_id": conversation_id,
                    "question_id": question_id,
                    "answer": analysis.get(
                        "answer",
                        "The requested additional evidence "
                        "was not found."
                    ),
                    "status": "insufficient_evidence",
                    "retrieval_rounds": retrieval_rounds,
                    "evidence_count": len(evidence),
                    "cached": False,
                }

            evidence = merge_evidence(
                evidence,
                new_evidence
            )

            print(
                f"LOGS: Total evidence after retrieval: "
                f"{len(evidence)}"
            )

            continue

        else:
            raise ValueError(
                f"Unexpected Analyst status: {status}"
            )


if __name__ == "__main__":
    q ="Extract the main experimental results table from the RoBERTa paper and identify which model achieved the best result on the GLUE benchmark.."
    res = process_source_question(
        ["/home/malak/Downloads/3ala_damanty/attension all you need paper.pdf",
        "/home/malak/Downloads/3ala_damanty/bert_pretrained.pdf",
        "/home/malak/Downloads/3ala_damanty/RoBERTa: A Robustly Optimized BERT Pretraining Approach.pdf"
        ] ,"file",q) 
    print(res)


#Extract the main experimental results table from the RoBERTa paper and identify which model achieved the best result on the GLUE benchmark.
# Why can removing the Next Sentence Prediction objective improve BERT-style pretraining? Explain the reasoning using evidence from the BERT and RoBERTa papers.


# Calculate the percentage difference in the number of parameters between BERT-base and BERT-large. Explain how this difference relates to their model configurations.