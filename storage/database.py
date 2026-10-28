# messages table 
# attempts table
# evaluation table
import sqlite3
from pathlib import Path
DB_PATH = Path().resolve().parent / "memory.sqlite3"

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection

def execute_query(query ,params=()):
    with get_connection() as conn:
        cursor = conn.execute(query,params)
        return cursor.lastrowid

def fetch_all(query, params=()):
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

def fetch_one(query, params=()):
    with get_connection() as conn:
        row = conn.execute(query, params).fetchone()
        return dict(row) if row else None



def init_db():
    with get_connection() as conn:
        conn.executescript("""
        Create table if not exists conversations (
        conversation_id TEXT PRIMARY KEY,
        created_at TEXT NOT NULL DEFAULT
        (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
        );

        create table if not exists questions(
        question_id TEXT PRIMARY KEY,
        conversation_id TEXT Not NULL,
        content TEXT NOT NULL,
        FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
        );

    CREATE TABLE IF NOT EXISTS attempts (
        attempt_id TEXT PRIMARY KEY,
        question_id TEXT NOT NULL,
        attempt_number INTEGER NOT NULL,
        answer TEXT NOT NULL,
        created_at TEXT NOT NULL DEFAULT
            (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (question_id, attempt_number),
        FOREIGN KEY (question_id) REFERENCES questions(question_id)  
    );

   CREATE TABLE IF NOT EXISTS evaluations (
        evaluation_id TEXT PRIMARY KEY,
        attempt_id TEXT NOT NULL,
        decision TEXT NOT NULL
            CHECK (decision IN ('accept', 'revise')),
        feedback TEXT NOT NULL,
        accuracy INTEGER NOT NULL
            CHECK (accuracy BETWEEN 1 AND 5),
        relevance INTEGER NOT NULL
            CHECK (relevance BETWEEN 1 AND 5),
        completeness INTEGER NOT NULL
            CHECK (completeness BETWEEN 1 AND 5),
        consistency INTEGER NOT NULL
            CHECK (consistency BETWEEN 1 AND 5),
        grounding INTEGER NOT NULL
            CHECK (grounding BETWEEN 1 AND 5),
        unsupported_claims INTEGER NOT NULL
            CHECK (unsupported_claims BETWEEN 1 AND 5),
        overall_quality INTEGER NOT NULL
            CHECK (overall_quality BETWEEN 1 AND 5),
        created_at TEXT NOT NULL DEFAULT
            (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        FOREIGN KEY (attempt_id) REFERENCES attempts(attempt_id) 
        ON DELETE CASCADE
    );

  
""")

