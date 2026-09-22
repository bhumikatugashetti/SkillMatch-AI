import sqlite3
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from services.job_matcher import normalize_skills

DB_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(DB_DIR, "skillmatch.db")

def _parse_skills_field(raw_field):
    """Safely parse JSON or raw string skills field from database into a list of normalized strings."""
    if not raw_field:
        return []
    try:
        parsed = json.loads(raw_field)
        return normalize_skills(parsed)
    except Exception:
        return normalize_skills(raw_field)

def get_db_connection():
    """Establish connection to SQLite database."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables if they do not exist."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analysis_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resume_filename TEXT NOT NULL,
            job_description TEXT NOT NULL,
            final_score REAL NOT NULL,
            keyword_score REAL NOT NULL,
            semantic_score REAL NOT NULL,
            matched_skills TEXT NOT NULL,
            missing_skills TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company_name TEXT NOT NULL,
            job_description TEXT NOT NULL,
            required_skills TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    
    # Auto-create demo recruiter account if it does not exist
    cursor.execute("SELECT * FROM users WHERE username = ?", ("recruiter",))
    if not cursor.fetchone():
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        password_hash = generate_password_hash("SkillMatch@2026")
        cursor.execute("""
            INSERT INTO users (username, password_hash, created_at)
            VALUES (?, ?, ?)
        """, ("recruiter", password_hash, created_at))

    conn.commit()
    conn.close()

def get_user_by_username(username):
    """Retrieve user record by username."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)

def get_user_by_id(user_id):
    """Retrieve user record by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    return dict(row)


def save_analysis(
    resume_filename,
    job_description,
    final_score,
    keyword_score,
    semantic_score,
    matched_skills,
    missing_skills
):
    """Save candidate-job match analysis result into SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    matched_json = json.dumps(normalize_skills(matched_skills))
    missing_json = json.dumps(normalize_skills(missing_skills))

    cursor.execute("""
        INSERT INTO analysis_history (
            resume_filename,
            job_description,
            final_score,
            keyword_score,
            semantic_score,
            matched_skills,
            missing_skills,
            created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        resume_filename,
        job_description,
        float(final_score),
        float(keyword_score),
        float(semantic_score),
        matched_json,
        missing_json,
        created_at
    ))

    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def _format_date(date_str):
    """Format stored datetime string into readable '18 Sep 2026' format."""
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y")
    except Exception:
        return date_str

def get_all_analyses():
    """Retrieve all candidate match analyses from database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_history ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    results = []
    for row in rows:
        matched = _parse_skills_field(row["matched_skills"])
        missing = _parse_skills_field(row["missing_skills"])
        results.append({
            "id": row["id"],
            "resume_filename": row["resume_filename"],
            "job_description": row["job_description"],
            "final_score": round(row["final_score"], 2),
            "keyword_score": round(row["keyword_score"], 2),
            "semantic_score": round(row["semantic_score"], 2),
            "matched_skills": matched,
            "missing_skills": missing,
            "created_at": row["created_at"],
            "date_formatted": _format_date(row["created_at"])
        })
    return results

def get_analysis_by_id(analysis_id):
    """Retrieve a single candidate match analysis by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM analysis_history WHERE id = ?", (analysis_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    matched = _parse_skills_field(row["matched_skills"])
    missing = _parse_skills_field(row["missing_skills"])

    return {
        "id": row["id"],
        "resume_filename": row["resume_filename"],
        "job_description": row["job_description"],
        "final_score": round(row["final_score"], 2),
        "keyword_score": round(row["keyword_score"], 2),
        "semantic_score": round(row["semantic_score"], 2),
        "matched_skills": matched,
        "missing_skills": missing,
        "created_at": row["created_at"],
        "date_formatted": _format_date(row["created_at"])
    }

def create_job(job_title, company_name, job_description, required_skills):
    """Save a new recruiter job posting into SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    skills_json = json.dumps(normalize_skills(required_skills))
    
    cursor.execute("""
        INSERT INTO jobs (
            job_title,
            company_name,
            job_description,
            required_skills,
            created_at
        ) VALUES (?, ?, ?, ?, ?)
    """, (
        job_title,
        company_name,
        job_description,
        skills_json,
        created_at
    ))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()
    return inserted_id

def get_all_jobs():
    """Retrieve all saved jobs from SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()

    jobs = []
    for row in rows:
        skills = _parse_skills_field(row["required_skills"])
        jobs.append({
            "id": row["id"],
            "job_title": row["job_title"],
            "company_name": row["company_name"],
            "job_description": row["job_description"],
            "required_skills": skills,
            "created_at": row["created_at"],
            "date_formatted": _format_date(row["created_at"])
        })
    return jobs

def get_job_by_id(job_id):
    """Retrieve a single job by ID."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM jobs WHERE id = ?", (job_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return None

    skills = _parse_skills_field(row["required_skills"])
    return {
        "id": row["id"],
        "job_title": row["job_title"],
        "company_name": row["company_name"],
        "job_description": row["job_description"],
        "required_skills": skills,
        "created_at": row["created_at"],
        "date_formatted": _format_date(row["created_at"])
    }

def update_job(job_id, job_title, company_name, job_description, required_skills):
    """Update an existing job description and required skills in SQLite database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    skills_json = json.dumps(normalize_skills(required_skills))

    cursor.execute("""
        UPDATE jobs
        SET job_title = ?,
            company_name = ?,
            job_description = ?,
            required_skills = ?
        WHERE id = ?
    """, (
        job_title,
        company_name,
        job_description,
        skills_json,
        job_id
    ))
    conn.commit()
    conn.close()

def delete_job(job_id):
    """Delete a job by ID from SQLite database using parameterized query."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
    conn.commit()
    conn.close()

def get_dashboard_stats():
    """Retrieve real statistics from database for Dashboard."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM jobs")
    job_count_row = cursor.fetchone()
    total_jobs = job_count_row[0] if job_count_row and job_count_row[0] is not None else 0

    cursor.execute("SELECT COUNT(*), AVG(final_score), MAX(final_score) FROM analysis_history")
    row = cursor.fetchone()

    total_analyses = row[0] if row and row[0] is not None else 0

    if total_analyses == 0:
        conn.close()
        return {
            "total_analyses": 0,
            "avg_score": 0.0,
            "highest_score": 0.0,
            "skill_gaps_detected": 0,
            "total_jobs": total_jobs,
            "has_data": False
        }

    avg_score = round(row[1], 2) if row[1] is not None else 0.0
    highest_score = round(row[2], 2) if row[2] is not None else 0.0

    # Calculate total skill gaps detected across all records
    cursor.execute("SELECT missing_skills FROM analysis_history")
    all_missing_rows = cursor.fetchall()
    conn.close()

    total_skill_gaps = 0
    for r in all_missing_rows:
        if r["missing_skills"]:
            missing_list = _parse_skills_field(r["missing_skills"])
            total_skill_gaps += len(missing_list)

    return {
        "total_analyses": total_analyses,
        "avg_score": avg_score,
        "highest_score": highest_score,
        "skill_gaps_detected": total_skill_gaps,
        "total_jobs": total_jobs,
        "has_data": True
    }

