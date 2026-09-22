import json
import re
from services.semantic_matcher import calculate_semantic_similarity
from services.skill_extractor import SKILLS_DATABASE

CANONICAL_SKILL_MAP = {
    skill.lower(): skill
    for skill in SKILLS_DATABASE
}

SKILL_WEIGHTS = {
    # Cloud
    "aws": 1.5,
    "ec2": 1.3,
    "s3": 1.2,
    "lambda": 1.2,
    "dynamodb": 1.2,
    "iam": 1.1,
    "cloudwatch": 1.1,
    "azure": 1.4,
    "google cloud": 1.4,

    # Programming
    "python": 1.3,
    "java": 1.2,
    "javascript": 1.1,

    # Database
    "sql": 1.3,
    "mysql": 1.1,
    "mongodb": 1.1,
    "postgresql": 1.1,

    # DevOps
    "docker": 1.3,
    "kubernetes": 1.4,
    "terraform": 1.3,
    "git": 1.0,
    "jenkins": 1.2,
    "linux": 1.1,

    # AI / Data
    "machine learning": 1.3,
    "artificial intelligence": 1.3,
    "nlp": 1.2,
    "pandas": 1.1,
    "numpy": 1.1,

    # Web
    "react": 1.1,
    "flask": 1.1,
    "node.js": 1.1
}

# Related skills that indicate knowledge of another skill
RELATED_SKILLS = {
    "aws": [
        "ec2",
        "s3",
        "lambda",
        "dynamodb",
        "iam",
        "cloudwatch"
    ],
    "git": [
        "github"
    ],
    "docker": [
        "kubernetes"
    ],
    "kubernetes": [
        "docker"
    ],
    "terraform": [
        "aws",
        "azure",
        "google cloud"
    ]
}


def normalize_skills(skills_input):
    """
    Normalizes candidate or required skills into a list of clean, unique skill strings.
    Handles:
    - Lists, sets, tuples
    - Single string (comma-separated, newline-separated)
    - JSON encoded strings or arrays
    - Whitespace normalization
    """
    if not skills_input:
        return []

    raw_list = []

    if isinstance(skills_input, str):
        str_val = skills_input.strip()
        if (str_val.startswith("[") and str_val.endswith("]")) or (str_val.startswith('"') and str_val.endswith('"')):
            try:
                parsed = json.loads(str_val)
                return normalize_skills(parsed)
            except Exception:
                pass
        raw_list = re.split(r'[,;\n]+', str_val)
    elif isinstance(skills_input, (list, set, tuple)):
        for item in skills_input:
            if isinstance(item, str):
                if ',' in item or '\n' in item or ';' in item:
                    raw_list.extend(re.split(r'[,;\n]+', item))
                else:
                    raw_list.append(item)
            elif item is not None:
                raw_list.append(str(item))
    else:
        raw_list = [str(skills_input)]

    seen = set()
    result = []
    for s in raw_list:
        cleaned = s.strip()
        if cleaned and cleaned.lower() not in seen:
            seen.add(cleaned.lower())
            result.append(format_skill_name(cleaned))

    return result


def format_skill_name(skill_str):
    """Format skill name to canonical casing if known, or title-cased if single word."""
    s_lower = skill_str.strip().lower()
    return CANONICAL_SKILL_MAP.get(s_lower, skill_str.strip())


def calculate_match(
    candidate_skills,
    required_skills,
    resume_text="",
    job_description=""
):
    norm_candidate = normalize_skills(candidate_skills)
    norm_required = normalize_skills(required_skills)

    candidate_skills_lower = {
        skill.lower()
        for skill in norm_candidate
    }

    matched_skills = set()
    missing_skills = set()

    total_weight = 0.0
    matched_weight = 0.0

    for req_skill in norm_required:
        req_lower = req_skill.lower()
        weight = SKILL_WEIGHTS.get(req_lower, 1.0)
        total_weight += weight

        # Exact skill match
        if req_lower in candidate_skills_lower:
            matched_skills.add(format_skill_name(req_skill))
            matched_weight += weight
            continue

        # Skill is not an exact match -> skill gap
        missing_skills.add(format_skill_name(req_skill))

        # Related skill match (provides partial score credit)
        related = RELATED_SKILLS.get(req_lower, [])
        for related_skill in related:
            if related_skill.lower() in candidate_skills_lower:
                matched_weight += (weight * 0.70)
                break

    if total_weight > 0:
        keyword_score = (matched_weight / total_weight) * 100.0
    else:
        keyword_score = 0.0

    if resume_text and job_description:
        semantic_score = calculate_semantic_similarity(
            resume_text,
            job_description
        )
    else:
        semantic_score = 0.0

    # Hybrid AI score (70% keyword + 30% semantic)
    final_score = (
        keyword_score * 0.70
        + semantic_score * 0.30
    )

    return {
        "score": round(final_score, 2),
        "keyword_score": round(keyword_score, 2),
        "semantic_score": round(semantic_score, 2),
        "matched": sorted(list(matched_skills)),
        "missing": sorted(list(missing_skills))
    }