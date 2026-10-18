"""
SQLite Database service for Multi-Agent AI Tutor.
Stores students, documents, document chunks, topics, validated questions,
quiz sessions, question attempts, mastery scores, and adaptive learning recommendations.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

DB_FILE = Path(__file__).resolve().parent.parent / "ai_tutor.db"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Initializes SQLite database tables and indexes."""
    os.makedirs(DB_FILE.parent, exist_ok=True)
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Students
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                grade TEXT DEFAULT 'Class 6',
                preferred_difficulty TEXT DEFAULT 'Medium',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 2. Documents
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                title TEXT NOT NULL,
                subject TEXT DEFAULT 'Mathematics',
                grade TEXT DEFAULT 'Class 6',
                page_count INTEGER NOT NULL,
                confidence_score REAL DEFAULT 1.0,
                extraction_notes TEXT,
                extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Document Chunks
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_chunks (
                chunk_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                page_number INTEGER NOT NULL,
                chunk_type TEXT DEFAULT 'text',
                content TEXT NOT NULL,
                bounding_box_json TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (document_id) ON DELETE CASCADE
            );
        """)

        # 4. Topics
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS topics (
                topic_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                learning_objectives_json TEXT,
                formulas_json TEXT,
                common_mistakes_json TEXT,
                solved_example TEXT,
                source_pages_json TEXT,
                FOREIGN KEY (document_id) REFERENCES documents (document_id) ON DELETE CASCADE
            );
        """)

        # 5. Questions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS questions (
                question_id TEXT PRIMARY KEY,
                document_id TEXT NOT NULL,
                topic_id TEXT,
                chapter TEXT NOT NULL,
                topic TEXT NOT NULL,
                question_type TEXT NOT NULL,
                question_text TEXT NOT NULL,
                difficulty TEXT DEFAULT 'Medium',
                marks INTEGER DEFAULT 1,
                options_json TEXT,
                correct_answer TEXT NOT NULL,
                accepted_alternatives_json TEXT,
                explanation TEXT NOT NULL,
                solution_steps_json TEXT,
                marking_rubric_json TEXT,
                diagram_reference TEXT,
                source_pages_json TEXT,
                source_chunk_ids_json TEXT,
                subquestions_json TEXT,
                matching_pairs_json TEXT,
                validation_status TEXT DEFAULT 'approved',
                validation_notes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (document_id) ON DELETE CASCADE
            );
        """)

        # 6. Quiz Sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quiz_sessions (
                session_id TEXT PRIMARY KEY,
                student_id TEXT NOT NULL,
                document_id TEXT NOT NULL,
                chapter_title TEXT NOT NULL,
                mode TEXT DEFAULT 'Practice Mode',
                total_marks INTEGER NOT NULL,
                current_score REAL DEFAULT 0.0,
                is_completed INTEGER DEFAULT 0,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                state_json TEXT,
                FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
                FOREIGN KEY (document_id) REFERENCES documents (document_id) ON DELETE CASCADE
            );
        """)

        # 7. Question Attempts
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_attempts (
                attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                student_id TEXT NOT NULL,
                question_id TEXT NOT NULL,
                student_answer TEXT,
                is_correct INTEGER NOT NULL,
                marks_awarded REAL NOT NULL,
                max_marks REAL NOT NULL,
                feedback TEXT,
                detailed_solution TEXT,
                is_arithmetic_mistake INTEGER DEFAULT 0,
                is_conceptual_misunderstanding INTEGER DEFAULT 0,
                attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES quiz_sessions (session_id) ON DELETE CASCADE,
                FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE,
                FOREIGN KEY (question_id) REFERENCES questions (question_id) ON DELETE CASCADE
            );
        """)

        # 8. Mastery Scores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS mastery_scores (
                student_id TEXT NOT NULL,
                topic_title TEXT NOT NULL,
                score_percentage REAL DEFAULT 0.0,
                attempts_count INTEGER DEFAULT 0,
                correct_count INTEGER DEFAULT 0,
                level TEXT DEFAULT 'Foundation',
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (student_id, topic_title),
                FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
            );
        """)

        # 9. Learning Recommendations
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS learning_recommendations (
                recommendation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                topic_title TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                priority TEXT DEFAULT 'Medium',
                suggested_action TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (student_id) REFERENCES students (student_id) ON DELETE CASCADE
            );
        """)

        # Create indices for fast lookup
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_doc ON document_chunks(document_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_topics_doc ON topics(document_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_doc ON questions(document_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_attempts_student ON question_attempts(student_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mastery_student ON mastery_scores(student_id);")
        
        # Ensure default student exists
        cursor.execute("SELECT student_id FROM students WHERE student_id = 'std_default';")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO students (student_id, name, grade, preferred_difficulty)
                VALUES ('std_default', 'Aarav Sharma', 'Class 6', 'Medium');
            """)

        conn.commit()


# ---------------- Student Operations ---------------- #

def get_or_create_student(student_id: str, name: str = "Aarav Sharma", grade: str = "Class 6") -> Dict[str, Any]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students WHERE student_id = ?", (student_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        cursor.execute(
            "INSERT INTO students (student_id, name, grade) VALUES (?, ?, ?)",
            (student_id, name, grade)
        )
        conn.commit()
        return {"student_id": student_id, "name": name, "grade": grade}


def list_students() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students ORDER BY created_at ASC")
        return [dict(r) for r in cursor.fetchall()]


def delete_student_history(student_id: str):
    """Deletes all quiz sessions, attempts, and mastery scores for a specific student."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM question_attempts WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM quiz_sessions WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM mastery_scores WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM learning_recommendations WHERE student_id = ?", (student_id,))
        conn.commit()


# ---------------- Document & Topic Operations ---------------- #

def save_document_analysis(analysis: Dict[str, Any], chunks: List[Dict[str, Any]]):
    with get_connection() as conn:
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO documents 
            (document_id, filename, title, subject, grade, page_count, confidence_score, extraction_notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis["document_id"],
            analysis["filename"],
            analysis["title"],
            analysis.get("subject", "Mathematics"),
            analysis.get("grade", "Class 6"),
            analysis["total_pages"],
            analysis.get("confidence_score", 1.0),
            analysis.get("extraction_notes", "")
        ))

        for c in chunks:
            cursor.execute("""
                INSERT OR REPLACE INTO document_chunks
                (chunk_id, document_id, page_number, chunk_type, content, bounding_box_json)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                c["chunk_id"],
                analysis["document_id"],
                c["page_number"],
                c.get("chunk_type", "text"),
                c["content"],
                json.dumps(c.get("bounding_box", []))
            ))

        for t in analysis.get("topics", []):
            cursor.execute("""
                INSERT OR REPLACE INTO topics
                (topic_id, document_id, title, description, learning_objectives_json, 
                 formulas_json, common_mistakes_json, solved_example, source_pages_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                t["topic_id"],
                analysis["document_id"],
                t["title"],
                t["description"],
                json.dumps(t.get("learning_objectives", [])),
                json.dumps(t.get("formulas", [])),
                json.dumps(t.get("common_mistakes", [])),
                t.get("solved_example", ""),
                json.dumps(t.get("source_pages", []))
            ))

        conn.commit()


def list_documents() -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents ORDER BY extracted_at DESC")
        return [dict(r) for r in cursor.fetchall()]


def get_document(document_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM documents WHERE document_id = ?", (document_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def get_document_topics(document_id: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM topics WHERE document_id = ?", (document_id,))
        rows = cursor.fetchall()
        topics = []
        for r in rows:
            d = dict(r)
            d["learning_objectives"] = json.loads(d["learning_objectives_json"] or "[]")
            d["formulas"] = json.loads(d["formulas_json"] or "[]")
            d["common_mistakes"] = json.loads(d["common_mistakes_json"] or "[]")
            d["source_pages"] = json.loads(d["source_pages_json"] or "[]")
            topics.append(d)
        return topics


def get_document_chunks(document_id: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM document_chunks WHERE document_id = ? ORDER BY page_number ASC", (document_id,))
        return [dict(r) for r in cursor.fetchall()]


# ---------------- Question Operations ---------------- #

def save_questions(questions: List[Dict[str, Any]]):
    with get_connection() as conn:
        cursor = conn.cursor()
        for q in questions:
            doc_id = q.get("document_id", "doc_default")
            chap = q.get("chapter", "Chapter")
            cursor.execute("SELECT document_id FROM documents WHERE document_id = ?", (doc_id,))
            if not cursor.fetchone():
                cursor.execute(
                    "INSERT OR IGNORE INTO documents (document_id, filename, title, page_count) VALUES (?, ?, ?, 1)",
                    (doc_id, f"{doc_id}.pdf", chap)
                )

            cursor.execute("""
                INSERT OR REPLACE INTO questions
                (question_id, document_id, topic_id, chapter, topic, question_type,
                 question_text, difficulty, marks, options_json, correct_answer,
                 accepted_alternatives_json, explanation, solution_steps_json,
                 marking_rubric_json, diagram_reference, source_pages_json,
                 source_chunk_ids_json, subquestions_json, matching_pairs_json,
                 validation_status, validation_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["question_id"],
                doc_id,
                q.get("topic_id"),
                chap,
                q.get("topic", "General"),
                q.get("question_type", "MCQ"),
                q.get("question_text", "Question"),
                q.get("difficulty", "Medium"),
                q.get("marks", 1),
                json.dumps(q.get("options", [])),
                q.get("correct_answer", ""),
                json.dumps(q.get("accepted_alternatives", [])),
                q.get("explanation", ""),
                json.dumps(q.get("solution_steps", [])),
                json.dumps(q.get("marking_rubric", [])),
                q.get("diagram_reference"),
                json.dumps(q.get("source_pages", [])),
                json.dumps(q.get("source_chunk_ids", [])),
                json.dumps(q.get("subquestions", [])),
                json.dumps(q.get("matching_pairs", {})),
                q.get("validation_status", "approved"),
                q.get("validation_notes", "")
            ))
        conn.commit()


def get_questions_by_filter(
    document_id: Optional[str] = None,
    topic: Optional[str] = None,
    difficulty: Optional[str] = None,
    question_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    query = "SELECT * FROM questions WHERE validation_status = 'approved'"
    params = []
    
    if document_id:
        query += " AND document_id = ?"
        params.append(document_id)
    if topic and topic != "All":
        query += " AND topic = ?"
        params.append(topic)
    if difficulty and difficulty != "Mixed":
        query += " AND difficulty = ?"
        params.append(difficulty)
    if question_type and question_type != "All":
        query += " AND question_type = ?"
        params.append(question_type)
        
    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(limit)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        
        parsed = []
        for r in rows:
            d = dict(r)
            d["options"] = json.loads(d["options_json"] or "[]")
            d["accepted_alternatives"] = json.loads(d["accepted_alternatives_json"] or "[]")
            d["solution_steps"] = json.loads(d["solution_steps_json"] or "[]")
            d["marking_rubric"] = json.loads(d["marking_rubric_json"] or "[]")
            d["source_pages"] = json.loads(d["source_pages_json"] or "[]")
            d["source_chunk_ids"] = json.loads(d["source_chunk_ids_json"] or "[]")
            d["subquestions"] = json.loads(d["subquestions_json"] or "[]")
            d["matching_pairs"] = json.loads(d["matching_pairs_json"] or "{}")
            parsed.append(d)
        return parsed


# ---------------- Quiz Sessions & Attempts ---------------- #

def save_quiz_session(session: Dict[str, Any]):
    sess_id = session["session_id"]
    std_id = session["student_id"]
    doc_id = session.get("document_id", "doc_default")
    chap = session.get("chapter_title", "Chapter")

    with get_connection() as conn:
        cursor = conn.cursor()

        # Ensure student exists
        cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (std_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)", (std_id, "Student"))

        # Ensure document exists
        cursor.execute("SELECT document_id FROM documents WHERE document_id = ?", (doc_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT OR IGNORE INTO documents (document_id, filename, title, page_count) VALUES (?, ?, ?, ?)",
                           (doc_id, f"{doc_id}.pdf", chap, 1))

        cursor.execute("""
            INSERT OR REPLACE INTO quiz_sessions
            (session_id, student_id, document_id, chapter_title, mode, total_marks,
             current_score, is_completed, start_time, end_time, state_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sess_id,
            std_id,
            doc_id,
            chap,
            session.get("mode", "Practice Mode"),
            session["total_marks"],
            session.get("current_score", 0.0),
            1 if session.get("is_completed", False) else 0,
            session.get("start_time"),
            session.get("end_time"),
            json.dumps(session)
        ))
        conn.commit()


def get_quiz_session(session_id: str) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quiz_sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row:
            return None
        d = dict(row)
        if d.get("state_json"):
            return json.loads(d["state_json"])
        return d


def record_question_attempt(attempt: Dict[str, Any]):
    """Records an individual question attempt and updates mastery score."""
    sess_id = attempt["session_id"]
    std_id = attempt["student_id"]
    q_id = attempt["question_id"]

    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Ensure student exists
        cursor.execute("SELECT student_id FROM students WHERE student_id = ?", (std_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)", (std_id, "Student"))

        # 2. Check if question exists or extract document_id
        cursor.execute("SELECT document_id, chapter FROM questions WHERE question_id = ?", (q_id,))
        q_row = cursor.fetchone()
        doc_id = attempt.get("document_id") or (q_row["document_id"] if q_row else "doc_default")
        chap = attempt.get("chapter") or (q_row["chapter"] if q_row else "Chapter")

        # 3. Ensure document exists
        cursor.execute("SELECT document_id FROM documents WHERE document_id = ?", (doc_id,))
        if not cursor.fetchone():
            cursor.execute("INSERT OR IGNORE INTO documents (document_id, filename, title, page_count) VALUES (?, ?, ?, ?)",
                           (doc_id, f"{doc_id}.pdf", chap, 1))

        # 4. Guarantee question exists in questions table to satisfy FOREIGN KEY constraint
        if not q_row:
            cursor.execute("""
                INSERT OR IGNORE INTO questions
                (question_id, document_id, chapter, topic, question_type,
                 question_text, correct_answer, explanation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q_id,
                doc_id,
                chap,
                attempt.get("topic", "General"),
                attempt.get("question_type", "Numerical"),
                attempt.get("question_text", "Question"),
                attempt.get("correct_answer", ""),
                attempt.get("detailed_solution") or attempt.get("explanation", "")
            ))

        # 5. Ensure session exists
        cursor.execute("SELECT session_id FROM quiz_sessions WHERE session_id = ?", (sess_id,))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT OR IGNORE INTO quiz_sessions 
                (session_id, student_id, document_id, chapter_title, total_marks)
                VALUES (?, ?, ?, ?, ?)
            """, (sess_id, std_id, doc_id, chap, 10))

        # 6. Insert Question Attempt
        cursor.execute("""
            INSERT INTO question_attempts
            (session_id, student_id, question_id, student_answer, is_correct,
             marks_awarded, max_marks, feedback, detailed_solution,
             is_arithmetic_mistake, is_conceptual_misunderstanding)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            sess_id,
            std_id,
            q_id,
            str(attempt.get("student_answer", "")),
            1 if attempt.get("is_correct") else 0,
            attempt.get("marks_awarded", 0.0),
            attempt.get("max_marks", 1.0),
            attempt.get("feedback", ""),
            attempt.get("detailed_solution", ""),
            1 if attempt.get("is_arithmetic_mistake") else 0,
            1 if attempt.get("is_conceptual_misunderstanding") else 0
        ))
        conn.commit()
    
    # Recalculate mastery for student & topic
    update_student_mastery_for_question(attempt["student_id"], attempt["question_id"])


def update_student_mastery_for_question(student_id: str, question_id: str):
    """Updates mastery score for the topic associated with this question."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT topic FROM questions WHERE question_id = ?", (question_id,))
        row = cursor.fetchone()
        if not row:
            return
        topic = row["topic"]

        # Aggregate attempts for this student on this topic
        cursor.execute("""
            SELECT COUNT(*) as total_attempts,
                   SUM(qa.is_correct) as total_correct,
                   SUM(qa.marks_awarded) as total_marks_earned,
                   SUM(qa.max_marks) as total_max_marks
            FROM question_attempts qa
            JOIN questions q ON qa.question_id = q.question_id
            WHERE qa.student_id = ? AND q.topic = ?
        """, (student_id, topic))
        stats = cursor.fetchone()
        
        if stats and stats["total_attempts"] > 0:
            total_attempts = stats["total_attempts"]
            total_correct = stats["total_correct"] or 0
            total_earned = stats["total_marks_earned"] or 0.0
            total_max = stats["total_max_marks"] or 1.0
            score_pct = round((total_earned / total_max) * 100.0, 1) if total_max > 0 else 0.0
            
            # Categorize Mastery
            if score_pct < 50.0:
                level = "Foundation"
            elif score_pct < 80.0:
                level = "Standard"
            else:
                level = "Mastery"

            cursor.execute("""
                INSERT OR REPLACE INTO mastery_scores
                (student_id, topic_title, score_percentage, attempts_count, correct_count, level, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (student_id, topic, score_pct, total_attempts, total_correct, level))
            
            # If Foundation level, generate targeted learning recommendation
            if level == "Foundation":
                cursor.execute("""
                    INSERT INTO learning_recommendations
                    (student_id, topic_title, recommendation, priority, suggested_action)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    student_id,
                    topic,
                    f"Performance on '{topic}' is {score_pct}%. Foundation concepts require revision.",
                    "High",
                    "Review basic definitions, solved examples, and practice 5 Easy questions."
                ))

            conn.commit()


def get_student_mastery(student_id: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM mastery_scores WHERE student_id = ? ORDER BY score_percentage ASC
        """, (student_id,))
        return [dict(r) for r in cursor.fetchall()]


def get_student_attempts(student_id: str, limit: int = 100) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT qa.*, q.question_text, q.topic, q.difficulty, q.question_type, q.chapter
            FROM question_attempts qa
            JOIN questions q ON qa.question_id = q.question_id
            WHERE qa.student_id = ?
            ORDER BY qa.attempt_time DESC
            LIMIT ?
        """, (student_id, limit))
        return [dict(r) for r in cursor.fetchall()]


def get_student_sessions(student_id: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM quiz_sessions WHERE student_id = ? ORDER BY start_time DESC
        """, (student_id,))
        return [dict(r) for r in cursor.fetchall()]


def get_student_recommendations(student_id: str) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM learning_recommendations 
            WHERE student_id = ? 
            ORDER BY created_at DESC LIMIT 5
        """, (student_id,))
        return [dict(r) for r in cursor.fetchall()]


# Initialize on import
init_db()
