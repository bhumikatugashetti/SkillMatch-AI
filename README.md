# SkillMatch AI

> **AI-Powered Recruitment & Skill Intelligence Platform**

SkillMatch AI is an intelligent recruitment SaaS platform designed to streamline candidate evaluation, job requirement analysis, and skill gap identification using natural language processing (NLP) and semantic AI embeddings.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [AI Architecture](#ai-architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Local Setup](#installation--local-setup)
- [Authentication & Local Demo Account](#authentication--local-demo-account)
- [Environment Variables](#environment-variables)
- [Production & Cloud Readiness](#production--cloud-readiness)
- [Health Check Endpoint](#health-check-endpoint)
- [Security Safeguards](#security-safeguards)
- [Automated Testing & Quality Assurance](#automated-testing--quality-assurance)

---

## 🎯 Overview

SkillMatch AI simplifies hiring workflows by automating candidate-job evaluation:

- **Extracts Technical Skills**: Automatically identifies technical skills from PDF resumes and job descriptions using custom regular expressions and bounded pattern matching.
- **Semantic Compatibility Scoring**: Combines keyword frequency analysis with deep Transformer vector embeddings (`all-MiniLM-L6-v2`) to produce a hybrid compatibility score.
- **Identifies Skill Gaps**: Pinpoints exact missing competencies and generates targeted technical interview questions.
- **Recruiter Job & Workflow Management**: Provides end-to-end job posting CRUD management, candidate ranking across multiple resumes, and persistent analysis history.

---

## ✨ Key Features

- **📄 Resume PDF Parsing & Skill Extraction**: Extract text from candidate resumes and detect technical skills without false positives.
- **💼 Recruiter Job Management**: Create, edit, list, and delete job postings with automatic skill extraction from job descriptions.
- **🎯 Candidate Job Matching**: Compare candidate resumes directly against target job postings to compute percentage compatibility.
- **🏆 Multi-Candidate Ranking**: Upload multiple PDF resumes simultaneously to evaluate and rank candidates in order of compatibility.
- **🧠 Skill Gap & AI Interview Question Generator**: Highlight missing skills and dynamically generate tailored interview questions.
- **📊 Real Statistics Dashboard**: View system-wide metrics (total jobs, total analyses, average compatibility score, skill gaps detected).
- **📜 Analysis History**: Access previous evaluations stored reliably in SQLite database.
- **🔐 Recruiter Session Authentication**: Secure recruiter endpoints with Flask sessions, Werkzeug password hashing, and `@login_required` decorators.
- **🛡️ Production Ready**: Hardened for deployment with Gunicorn WSGI support, custom 404/500 pages, `secure_filename` checks, 16MB upload limits, and `/health` monitoring.

---

## 🧠 AI Architecture

```
                                  [ Candidate Resume PDF ]
                                             │
                                             ▼
                                   ( PDF Text Extraction )
                                             │
                                             ▼
                                   ( Skill Extraction )
                                             │
                                             ▼
                                    Candidate Profile
                                             │
 ┌───────────────────────────────────────────┴───────────────────────────────────────────┐
 │                                                                                       │
 ▼                                                                                       ▼
[ Keyword Frequency Match ]                                                [ Semantic Embeddings Match ]
 (Exact & Regex Match)                                                      (SentenceTransformers Cosine)
 │                                                                                       │
 └───────────────────────────────────────────┬───────────────────────────────────────────┘
                                             │
                                             ▼
                              [ Hybrid Compatibility Score ]
                                             │
                                             ▼
                          [ Skill Gap Analysis & AI Questions ]
                                             │
                                             ▼
                               [ SQLite History & Dashboard ]
```

---

## 🛠️ Technology Stack

### Current Application Stack
- **Core Backend**: Python 3.x, Flask
- **WSGI Production Server**: Gunicorn
- **Database**: SQLite (via Python `sqlite3`)
- **Machine Learning & NLP**:
  - `sentence-transformers` (`all-MiniLM-L6-v2`)
  - `scikit-learn` (Cosine Similarity)
  - `pandas` & `numpy`
- **PDF Extraction**: `pdfplumber`
- **Security & Session**: `Werkzeug` (Password Hashing, Secure Filename)
- **Frontend**: HTML5, CSS3 (Vanilla CSS with CSS variables, Glassmorphism, Responsive Grid), JavaScript (Vanilla JS)

### Planned Cloud Deployment Architecture
- **Cloud Provider**: Amazon Web Services (AWS)
- **Compute**: AWS EC2 / ECS
- **WSGI Gateway**: Gunicorn + Nginx
- **Storage & Database**: AWS S3 (Resumes), AWS RDS / DynamoDB (Future Scaling)

---

## 📁 Project Structure

```
SkillMatch-AI/
├── app.py                      # Main Flask application & routes
├── requirements.txt            # Python dependencies (incl. Gunicorn)
├── README.md                   # Project documentation
├── .gitignore                  # Git ignore rules
│
├── database/
│   └── db.py                   # SQLite database initialization & CRUD queries
│
├── services/
│   ├── skill_extractor.py      # Regex-based skill extraction engine
│   ├── semantic_matcher.py     # SentenceTransformer embedding & cosine similarity
│   ├── job_matcher.py          # Hybrid score calculation (Keyword + Semantic)
│   └── interview_generator.py  # AI interview question generation
│
├── static/
│   ├── css/
│   │   └── style.css           # Global stylesheet & design system
│   └── js/
│       └── script.js           # Client-side UI interactions
│
├── templates/
│   ├── index.html              # Public landing page
│   ├── login.html              # Recruiter login page
│   ├── dashboard.html          # Metrics & recruitment analytics
│   ├── jobs.html               # Recruiter job list
│   ├── job_create.html         # Job creation form
│   ├── job_detail.html         # Detailed job posting view
│   ├── job_edit.html           # Job edit form
│   ├── upload.html             # Resume upload page
│   ├── resume_result.html      # Resume skill analysis result
│   ├── job.html                # Standalone job description analyzer
│   ├── job_result.html         # Standalone job analysis result
│   ├── match.html              # Candidate-job matching page
│   ├── match_result.html       # Candidate match breakdown & interview questions
│   ├── ranking.html            # Candidate ranking upload form
│   ├── ranking_result.html     # Candidate ranking leaderboard
│   ├── history.html            # Evaluation history page
│   ├── history_detail.html     # Historical evaluation detail view
│   ├── 404.html                # Page not found error page
│   └── 500.html                # Server error page
│
└── uploads/
    └── resumes/
        └── .gitkeep            # Upload directory placeholder (PDFs ignored)
```

---

## 🚀 Installation & Local Setup

### Prerequisites
- Python 3.9+ installed on Windows / Linux / macOS.

### Windows Setup Instructions

1. **Clone or navigate to the project directory**:
   ```cmd
   cd C:\Users\LPF\Desktop\projects\SkillMatch-AI
   ```

2. **Create and activate a virtual environment**:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```cmd
   pip install -r requirements.txt
   ```

4. **Run the local development server**:
   ```cmd
   python app.py
   ```

5. **Access the application**:
   Open your browser and navigate to:
   - Application Home: `http://127.0.0.1:5000/`
   - Health Check: `http://127.0.0.1:5000/health`

---

## 🔐 Authentication & Local Demo Account

The application enforces session-based recruiter authentication for all administrative and matching tools.

### Local Development Demo Account

> [!NOTE]
> The database automatically seeds a demo recruiter account on first startup for local testing.

- **Username**: `recruiter`
- **Password**: `SkillMatch@2026`

*Production Warning*: Demo credentials must be disabled in production deployments, and authentication should be integrated with an enterprise IAM or secrets management system.

---

## ⚙️ Environment Variables

Configure application behavior using environment variables:

| Variable | Description | Default (Local Dev) |
| :--- | :--- | :--- |
| `FLASK_SECRET_KEY` | Secret key used for signing session cookies. | Development fallback string |
| `FLASK_DEBUG` | Enables/disables Flask debug mode (`True` / `False`). | `True` for `python app.py` |

---

## 🏭 Production & Cloud Readiness

### Local Development Server
```bash
python app.py
```

### Production WSGI Execution (Gunicorn for Linux / AWS)
```bash
gunicorn app:app
```

When started with Gunicorn, debug mode is automatically disabled (`FLASK_DEBUG=False`).

---

## 🏥 Health Check Endpoint

Monitoring services and AWS Load Balancers can check application health at:

- **Endpoint**: `GET /health`
- **HTTP Status**: `200 OK`
- **Response**:
  ```json
  {
    "service": "SkillMatch AI",
    "status": "healthy"
  }
  ```

This endpoint does not expose credentials, database connections, or internal server paths.

---

## 🛡️ Security Safeguards

- **Password Hashing**: Passwords stored as Werkzeug `scrypt`/`pbkdf2` hashes.
- **Session Protection**: Recruiter endpoints protected with `@login_required` decorators.
- **File Upload Security**:
  - `secure_filename()` sanitizes uploaded filenames against path traversal.
  - Strict case-insensitive `.pdf` extension validation.
  - Maximum upload size capped at `16 MB` (`MAX_CONTENT_LENGTH`).
- **Parameterized SQL Queries**: All SQLite database interactions use parameterized `?` bindings to prevent SQL injection.
- **Sanitized Logging**: Server logs capture application lifecycle events without logging passwords, secrets, or raw resume contents.
- **Error Protection**: Custom 404 and 500 error templates prevent exposing internal Python stack traces to end users.

---

## 🧪 Automated Testing & Quality Assurance

The application includes automated test suites covering:

1. **Authentication Flow**: Validates credential checking, session creation, logout, and protected route redirection.
2. **Job Management CRUD**: Tests job creation, skill extraction, updates, and safe deletion.
3. **Health Check & Security**: Tests `/health` JSON structure, non-PDF file rejection, and 404/500 template rendering.
4. **Skill Extractor Regression Guard**:
   - Strictly verifies that standalone skill `"C"` is **NOT** falsely detected from words like `"Cloud"`, `"CSS"`, or `"CI/CD"`.
