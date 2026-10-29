from storage.database import execute_query

def save_question(question_id: str,conversation_id: str,content: str):
    if not question_id or not conversation_id or not content:
        raise ValueError("question_id, conversation_id, and content must be provided.")
    query="""
        INSERT INTO questions (question_id, conversation_id, content)
        VALUES (?, ?, ?)
    """
    execute_query(query, (question_id, conversation_id, content,))
    print(f"Saved question: {question_id}, conversation_id: {conversation_id}, content: {content}")


def save_attempt(attempt_id: str, question_id: str, attempt_number: int, answer: str):
    if not attempt_id or not question_id or attempt_number is None or not answer:
        raise ValueError("attempt_id, question_id, attempt_number, and answer must be provided.")
    query="""
        INSERT INTO attempts (attempt_id, question_id, attempt_number, answer)
        VALUES (?, ?, ?, ?)
    """
    execute_query(query, (attempt_id, question_id, attempt_number, answer,))
    print(f"Saved attempt: {attempt_id}, question_id: {question_id}, attempt_number: {attempt_number}, answer: {answer}")


def get_attempts_count(question_id: str) -> int:
    if not question_id:
        raise ValueError("question_id must be provided.")
    query = """
        SELECT COUNT(*) as count FROM attempts WHERE question_id = ?
    """
    result = execute_query(query, (question_id,))
    return result if result else 0

def get_chat_history(conversation_id):
    if not conversation_id:
        raise ValueError("conversation_id must be provided.")
    query = """
        SELECT
            q.question_id,
            q.content AS question,
            a.attempt_number,
            a.answer,
            a.created_at
        FROM questions AS q
        JOIN attempts AS a
            ON a.question_id = q.question_id
        WHERE q.conversation_id = ?
        ORDER BY q.question_id ASC, a.attempt_number ASC
    """
    rows= execute_query(query, (conversation_id,))
    return rows 

def create_conversation(conversation_id: str):
    if not conversation_id:
        raise ValueError("conversation_id must be provided.")
    query = """
        INSERT INTO conversations (conversation_id)
        VALUES (?)
    """
    execute_query(query, (conversation_id,))
    print(f"Created conversation: {conversation_id}")


            
        