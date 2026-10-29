from storage.database import execute_query, fetch_all, fetch_one

def save_evaluation(
        evaluation_id,
        attempt_id,
        decision,
        feedback,
        accuracy,
        relevance,
        completeness,
        consistency,
        grounding,
        unsupported_claims,
        overall_quality,):
    query = """
            INSERT INTO evaluations (
            evaluation_id,
            attempt_id,
            decision,
            feedback,
            accuracy,
            relevance,
            completeness,
            consistency,
            grounding,
            unsupported_claims,
            overall_quality
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    execute_query(query, (evaluation_id, attempt_id, decision, feedback, accuracy, relevance, completeness, consistency, grounding, unsupported_claims, overall_quality))

def get_evaluations_by_attempt(attempt_id):
    query = """
        SELECT * FROM evaluations WHERE attempt_id = ?
    """
    return fetch_all(query, (attempt_id,))

def get_evaluations(question_id):
    query = """
        SELECT
            a.attempt_number,
            e.evaluation_id,
            e.attempt_id,
            e.decision,
            e.feedback,
            e.accuracy,
            e.relevance,
            e.completeness,
            e.consistency,
            e.grounding,
            e.unsupported_claims,
            e.overall_quality,
            e.created_at
        FROM evaluations AS e
        JOIN attempts AS a
            ON e.attempt_id = a.attempt_id
        WHERE a.question_id = ?
        ORDER BY a.attempt_number
    """

    return fetch_all(query, (question_id,))
