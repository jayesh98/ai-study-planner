import sqlite3
from datetime import date

DB_NAME = "study_planner.db"

def get_db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_tables():
    conn = get_db()
    cur = conn.cursor()

    # Users table (already created in auth, but safe to keep)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL
        )
    """)

    # Subjects per user
    cur.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            subject_name TEXT,
            is_weak INTEGER
        )
    """)

    # Study logs per user
    cur.execute("""
        CREATE TABLE IF NOT EXISTS study_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            subject_name TEXT,
            study_date TEXT,
            planned_hours REAL,
            actual_hours REAL
        )
    """)

    conn.commit()
    conn.close()

# ---------------- SUBJECT FUNCTIONS ----------------

def save_subject(user_email, subject_name, is_weak):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO subjects (user_email, subject_name, is_weak) VALUES (?, ?, ?)",
        (user_email, subject_name, int(is_weak))
    )
    conn.commit()
    conn.close()

def get_subjects(user_email):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "SELECT subject_name, is_weak FROM subjects WHERE user_email=?",
        (user_email,)
    )
    data = cur.fetchall()
    conn.close()
    return data

def clear_subjects(user_email):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM subjects WHERE user_email=?",
        (user_email,)
    )
    conn.commit()
    conn.close()

# ---------------- STUDY LOG FUNCTIONS ----------------

def save_study_log(user_email, subject, planned, actual):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO study_logs 
        (user_email, subject_name, study_date, planned_hours, actual_hours)
        VALUES (?, ?, ?, ?, ?)
        """,
        (user_email, subject, str(date.today()), planned, actual)
    )
    conn.commit()
    conn.close()

def get_study_logs(user_email):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT study_date, subject_name, planned_hours, actual_hours
        FROM study_logs
        WHERE user_email=?
        """,
        (user_email,)
    )
    rows = cur.fetchall()
    conn.close()

    return rows
