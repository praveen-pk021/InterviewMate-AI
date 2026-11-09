
import sqlite3
import json
from datetime import datetime

DB_NAME = "interview_history.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            score REAL NOT NULL,
            summary TEXT,
            strengths TEXT,
            improvements TEXT,
            ideal_answer TEXT,
            verdict TEXT,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def save_attempt(category, difficulty, question, answer, result):

    conn = get_connection()

    conn.execute("""
        INSERT INTO interviews (
            category,
            difficulty,
            question,
            answer,
            score,
            summary,
            strengths,
            improvements,
            ideal_answer,
            verdict,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        category,
        difficulty,
        question,
        answer,
        result["score"],
        result["summary"],
        json.dumps(result["strengths"]),
        json.dumps(result["improvements"]),
        result["ideal_answer"],
        result["verdict"],
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()


def get_attempts():

    conn = get_connection()
    conn.row_factory = sqlite3.Row

    rows = conn.execute("""
        SELECT * FROM interviews
        ORDER BY id ASC
    """).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_statistics():

    attempts = get_attempts()

    if not attempts:
        return {
            "total": 0,
            "average": 0,
            "latest": 0,
            "improvement": 0
        }

    scores = [float(item["score"]) for item in attempts]

    average = sum(scores) / len(scores)
    latest = scores[-1]

    improvement = (
        scores[-1] - scores[-2]
        if len(scores) >= 2
        else 0
    )

    return {
        "total": len(scores),
        "average": round(average, 2),
        "latest": round(latest, 2),
        "improvement": round(improvement, 2)
    }
