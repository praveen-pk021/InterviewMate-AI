
import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).with_name("interview_history.db")


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = _connect()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                category TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                score REAL NOT NULL,
                verdict TEXT,
                summary TEXT,
                strengths TEXT,
                improvements TEXT,
                ideal_answer TEXT
            )
        """)
        conn.commit()
    finally:
        conn.close()


def save_attempt(category, difficulty, question, answer, result):
    conn = _connect()
    try:
        conn.execute(
            """
            INSERT INTO attempts (
                created_at, category, difficulty, question, answer,
                score, verdict, summary, strengths, improvements, ideal_answer
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                category,
                difficulty,
                question,
                answer,
                float(result["score"]),
                result.get("verdict"),
                result.get("summary"),
                json.dumps(result.get("strengths", [])),
                json.dumps(result.get("improvements", [])),
                result.get("ideal_answer"),
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_attempts():
    conn = _connect()
    try:
        rows = conn.execute(
            "SELECT * FROM attempts ORDER BY id ASC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_statistics():
    attempts = get_attempts()

    if not attempts:
        return {
            "total": 0,
            "average": 0.0,
            "latest": 0.0,
            "improvement": 0.0,
        }

    scores = [float(item["score"]) for item in attempts]
    latest = scores[-1]
    previous = scores[-2] if len(scores) > 1 else latest

    return {
        "total": len(scores),
        "average": sum(scores) / len(scores),
        "latest": latest,
        "improvement": latest - previous,
    }
