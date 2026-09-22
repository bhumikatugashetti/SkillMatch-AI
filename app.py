from flask import Flask, render_template, request, redirect, url_for, session
import os
import pdfplumber
import logging
from functools import wraps
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename

from services.skill_extractor import extract_skills
from services.job_matcher import calculate_match
from services.interview_generator import generate_interview_questions
from database.db import (
    init_db,
    save_analysis,
    get_all_analyses,
    get_analysis_by_id,
    get_dashboard_stats,
    create_job,
    get_all_jobs,
    get_job_by_id,
    update_job,
    delete_job,
    get_user_by_username,
    get_user_by_id
)

# ============================================================
# APPLICATION LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("skillmatch_ai")

logger.info("Initializing SkillMatch AI application...")

app = Flask(__name__)

# Secret key for Flask sessions
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "skillmatch-ai-secret-key-2026")

# Maximum upload limit: 16 MB
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

# Initialize SQLite database
init_db()


# ============================================================
# LOGIN REQUIRED DECORATOR
# ============================================================

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            logger.info("Unauthenticated access attempt redirected to login.")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


# ============================================================
# UPLOAD FOLDER
# ============================================================

UPLOAD_FOLDER = "uploads/resumes"

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ============================================================
# HEALTH CHECK ENDPOINT (FOR MONITORING / LOAD BALANCERS)
# ============================================================

@app.route("/health")
def health_check():
    """Simple production health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "SkillMatch AI"
    }, 200


# ============================================================
# ERROR HANDLERS (PRODUCTION SAFE)
# ============================================================

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Internal Server Error: {e}", exc_info=True)
    return render_template("500.html"), 500


@app.errorhandler(413)
def request_entity_too_large(e):
    logger.warning("File upload size exceeded maximum allowed limit (16MB).")
    return "File size exceeds maximum allowed limit (16MB).", 413


# ============================================================
# AUTHENTICATION ROUTES
# ============================================================

@app.route("/login", methods=["GET", "POST"])
def login():
    if "user_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "GET":
        return render_template("login.html")

    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not username or not password:
        logger.warning("Login attempt with missing username or password.")
        return render_template(
            "login.html",
            error="Please enter both username and password.",
            username=username
        ), 400

    user = get_user_by_username(username)

    if not user or not check_password_hash(user["password_hash"], password):
        logger.warning(f"Failed login attempt for username: {username}")
        return render_template(
            "login.html",
            error="Invalid username or password.",
            username=username
        ), 401

    session.clear()
    session["user_id"] = user["id"]
    session["username"] = user["username"]

    logger.info(f"Successful recruiter login for user: {username}")
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    username = session.get("username", "Unknown")
    session.clear()
    logger.info(f"Recruiter logged out: {username}")
    return redirect(url_for("login"))


# ============================================================
# HOME PAGE
# ============================================================

@app.route("/")
def home():
    return render_template("index.html")


# ============================================================
# RESUME UPLOAD PAGE
# ============================================================

@app.route("/upload")
@login_required
def upload_page():
    return render_template("upload.html")


# ============================================================
# RESUME ANALYSIS
# ============================================================

@app.route("/analyze", methods=["POST"])
@login_required
def analyze_resume():

    if "resume" not in request.files:
        return "No resume uploaded.", 400

    resume = request.files["resume"]

    if resume.filename == "":
        return "Please select a resume file.", 400

    if not resume.filename.lower().endswith(".pdf"):
        logger.warning(f"Rejected non-PDF upload attempt: {resume.filename}")
        return "Invalid file format. Only PDF files are accepted.", 400

    safe_filename = secure_filename(resume.filename)
    if not safe_filename:
        safe_filename = "resume.pdf"

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        safe_filename
    )

    resume.save(file_path)

    extracted_text = ""

    try:

        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    extracted_text += text + "\n"

    except Exception as e:
        logger.error(f"Error reading PDF file {safe_filename}: {e}")
        return f"Error reading PDF file: {e}", 400

    if not extracted_text.strip():
        logger.warning(f"Uploaded PDF file contains no readable text: {safe_filename}")
        return "Uploaded PDF file contains no readable text.", 400

    detected_skills = extract_skills(extracted_text)
    logger.info(f"Resume analysis completed for file: {safe_filename}")

    return render_template(
        "resume_result.html",
        filename=safe_filename,
        extracted_text=extracted_text,
        skills=detected_skills
    )


# ============================================================
# JOB DESCRIPTION PAGE
# ============================================================

@app.route("/job")
@login_required
def job_page():
    return render_template("job.html")


# ============================================================
# JOB DESCRIPTION ANALYSIS
# ============================================================

@app.route("/job/analyze", methods=["POST"])
@login_required
def analyze_job():

    job_description = request.form.get(
        "job_description",
        ""
    )

    if not job_description.strip():
        return "Please enter a job description.", 400

    required_skills = extract_skills(job_description)
    logger.info("Job description analysis completed.")

    return render_template(
        "job_result.html",
        job_description=job_description,
        required_skills=required_skills
    )


# ============================================================
# CANDIDATE JOB MATCHING
# ============================================================

@app.route("/match", methods=["GET", "POST"])
@login_required
def match_candidate():

    if request.method == "GET":
        job_id = request.args.get("job_id")
        prefill_job_description = ""
        selected_job_title = ""
        if job_id:
            try:
                job = get_job_by_id(int(job_id))
                if job:
                    prefill_job_description = job["job_description"]
                    selected_job_title = job["job_title"]
            except ValueError:
                pass
        return render_template(
            "match.html",
            prefill_job_description=prefill_job_description,
            selected_job_title=selected_job_title
        )

    if "resume" not in request.files:
        return "No resume uploaded.", 400

    resume = request.files["resume"]

    if resume.filename == "":
        return "Please select a resume file.", 400

    if not resume.filename.lower().endswith(".pdf"):
        logger.warning(f"Rejected non-PDF candidate match upload: {resume.filename}")
        return "Invalid file format. Only PDF files are accepted.", 400

    job_description = request.form.get(
        "job_description",
        ""
    )

    if job_description.strip() == "":
        return "Please enter a job description.", 400

    safe_filename = secure_filename(resume.filename)
    if not safe_filename:
        safe_filename = "resume.pdf"

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        safe_filename
    )

    resume.save(file_path)

    extracted_text = ""

    try:
        with pdfplumber.open(file_path) as pdf:

            for page in pdf.pages:

                text = page.extract_text()

                if text:
                    extracted_text += text + "\n"

    except Exception as e:
        logger.error(f"Error reading candidate PDF {safe_filename}: {e}")
        return f"Error reading PDF file: {e}", 400

    if not extracted_text.strip():
        return "Uploaded candidate PDF contains no readable text.", 400

    candidate_skills = extract_skills(
        extracted_text
    )

    required_skills = extract_skills(
        job_description
    )

    match_result = calculate_match(
        candidate_skills,
        required_skills,
        extracted_text,
        job_description
    )

    interview_questions = generate_interview_questions(
        required_skills,
        match_result["missing"]
    )

    # Save candidate analysis result to SQLite database
    save_analysis(
        resume_filename=safe_filename,
        job_description=job_description,
        final_score=match_result["score"],
        keyword_score=match_result["keyword_score"],
        semantic_score=match_result["semantic_score"],
        matched_skills=match_result["matched"],
        missing_skills=match_result["missing"]
    )

    logger.info(f"Candidate matching calculated successfully for file: {safe_filename}")

    return render_template(
        "match_result.html",
        filename=safe_filename,
        score=match_result["score"],
        keyword_score=match_result["keyword_score"],
        semantic_score=match_result["semantic_score"],
        matched_skills=match_result["matched"],
        missing_skills=match_result["missing"],
        candidate_skills=candidate_skills,
        required_skills=required_skills,
        interview_questions=interview_questions
    )


# ============================================================
# RECRUITER JOB MANAGEMENT
# ============================================================

@app.route("/jobs")
@login_required
def list_jobs():
    jobs = get_all_jobs()
    return render_template("jobs.html", jobs=jobs)


@app.route("/jobs/create", methods=["GET", "POST"])
@login_required
def job_create():
    if request.method == "GET":
        return render_template("job_create.html")

    job_title = request.form.get("job_title", "").strip()
    company_name = request.form.get("company_name", "").strip()
    job_description = request.form.get("job_description", "").strip()

    if not job_title or not company_name or not job_description:
        return "Please fill in all job details.", 400

    required_skills = extract_skills(job_description)
    job_id = create_job(
        job_title=job_title,
        company_name=company_name,
        job_description=job_description,
        required_skills=required_skills
    )

    logger.info(f"New job created with ID {job_id}: {job_title}")
    return redirect(url_for("job_detail", job_id=job_id))


@app.route("/jobs/<int:job_id>")
@login_required
def job_detail(job_id):
    job = get_job_by_id(job_id)
    if not job:
        return "Job not found.", 404
    return render_template("job_detail.html", job=job)


@app.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def job_edit(job_id):
    job = get_job_by_id(job_id)
    if not job:
        return "Job not found.", 404

    if request.method == "GET":
        return render_template("job_edit.html", job=job)

    job_title = request.form.get("job_title", "").strip()
    company_name = request.form.get("company_name", "").strip()
    job_description = request.form.get("job_description", "").strip()

    if not job_title or not company_name or not job_description:
        return "Please fill in all job details.", 400

    required_skills = extract_skills(job_description)
    update_job(
        job_id=job_id,
        job_title=job_title,
        company_name=company_name,
        job_description=job_description,
        required_skills=required_skills
    )

    logger.info(f"Job ID {job_id} updated successfully.")
    return redirect(url_for("job_detail", job_id=job_id))


@app.route("/jobs/<int:job_id>/delete", methods=["GET", "POST"])
@login_required
def job_delete(job_id):
    job = get_job_by_id(job_id)
    if not job:
        return "Job not found.", 404
    delete_job(job_id)
    logger.info(f"Job ID {job_id} deleted successfully.")
    return redirect(url_for("list_jobs"))


# ============================================================
# RECRUITMENT DASHBOARD
# ============================================================

@app.route("/dashboard")
@login_required
def dashboard():
    stats = get_dashboard_stats()
    all_history = get_all_analyses()
    recent_analyses = all_history[:5] if stats["has_data"] else []
    return render_template(
        "dashboard.html",
        stats=stats,
        recent_analyses=recent_analyses
    )


# ============================================================
# ANALYSIS HISTORY PAGE
# ============================================================

@app.route("/history")
@login_required
def analysis_history():
    analyses = get_all_analyses()
    return render_template(
        "history.html",
        analyses=analyses
    )


# ============================================================
# HISTORY DETAIL PAGE
# ============================================================

@app.route("/history/<int:analysis_id>")
@login_required
def history_detail(analysis_id):
    analysis = get_analysis_by_id(analysis_id)
    if not analysis:
        return "Analysis record not found.", 404

    # Regenerate interview questions based on stored skill gaps
    all_required_skills = list(set(analysis["matched_skills"] + analysis["missing_skills"]))
    interview_questions = generate_interview_questions(
        all_required_skills,
        analysis["missing_skills"]
    )

    return render_template(
        "history_detail.html",
        analysis=analysis,
        interview_questions=interview_questions
    )


# ============================================================
# CANDIDATE RANKING
# ============================================================

@app.route("/ranking", methods=["GET", "POST"])
@login_required
def rank_candidates():

    if request.method == "GET":
        return render_template("ranking.html")

    job_description = request.form.get(
        "job_description",
        ""
    )

    if job_description.strip() == "":
        return "Please enter a job description.", 400

    resumes = request.files.getlist("resumes")

    if not resumes:
        return "Please upload at least one resume.", 400

    required_skills = extract_skills(
        job_description
    )

    candidates = []

    for resume in resumes:

        if resume.filename == "":
            continue

        if not resume.filename.lower().endswith(".pdf"):
            continue

        safe_filename = secure_filename(resume.filename)
        if not safe_filename:
            safe_filename = "resume.pdf"

        file_path = os.path.join(
            app.config["UPLOAD_FOLDER"],
            safe_filename
        )

        resume.save(file_path)

        extracted_text = ""

        try:

            with pdfplumber.open(file_path) as pdf:

                for page in pdf.pages:

                    text = page.extract_text()

                    if text:
                        extracted_text += text + "\n"

        except Exception as e:
            logger.error(f"Error reading ranking PDF {safe_filename}: {e}")
            continue

        candidate_skills = extract_skills(
            extracted_text
        )

        result = calculate_match(
            candidate_skills,
            required_skills,
            extracted_text,
            job_description
        )

        candidates.append({

            "filename": safe_filename,

            "score": result["score"],

            "matched": result["matched"],

            "missing": result["missing"]

        })

    candidates.sort(
        key=lambda candidate: candidate["score"],
        reverse=True
    )

    logger.info(f"Candidate ranking completed for {len(candidates)} candidates.")

    return render_template(
        "ranking_result.html",
        candidates=candidates
    )


# ============================================================
# RUN APPLICATION (LOCAL DEVELOPMENT ENTRY POINT)
# ============================================================

if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG", "True").lower() in ["true", "1"]
    logger.info(f"Starting Flask local development server (debug={debug_mode})...")
    app.run(debug=debug_mode)