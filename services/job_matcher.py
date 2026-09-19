# ============================================================
# SKILLMATCH AI - INTELLIGENT JOB MATCHING ENGINE
# ============================================================

from services.semantic_matcher import calculate_semantic_similarity


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

def calculate_match(
    candidate_skills,
    required_skills,
    resume_text,
    job_description
):

    candidate_skills_lower = {
        skill.lower()
        for skill in candidate_skills
    }

    required_skills_lower = {
        skill.lower()
        for skill in required_skills
    }


    matched_skills = set()

    partially_matched_skills = set()

    missing_skills = set()


    total_weight = 0
    matched_weight = 0


    for skill in required_skills_lower:

        weight = SKILL_WEIGHTS.get(
            skill,
            1.0
        )

        total_weight += weight


        # Exact skill match
        if skill in candidate_skills_lower:

            matched_skills.add(skill)

            matched_weight += weight

            continue


        # Related skill match
        related = RELATED_SKILLS.get(
            skill,
            []
        )

        related_found = False

        for related_skill in related:

            if related_skill in candidate_skills_lower:

                partially_matched_skills.add(
                    skill
                )

                matched_weight += (
                    weight * 0.70
                )

                related_found = True

                break


        if not related_found:

            missing_skills.add(skill)


    if total_weight > 0:

        keyword_score = (
            matched_weight
            / total_weight
        ) * 100

    else:

        keyword_score = 0


    semantic_score = calculate_semantic_similarity(
        resume_text,
        job_description
    )


    # Hybrid AI score
    final_score = (
        keyword_score * 0.70
        +
        semantic_score * 0.30
    )


    # Combine exact and related matches
    all_matched_skills = (
        matched_skills
        | partially_matched_skills
    )


    return {

        "score": round(
            final_score,
            2
        ),

        "keyword_score": round(
            keyword_score,
            2
        ),

        "semantic_score": round(
            semantic_score,
            2
        ),

        "matched": sorted(
            all_matched_skills
        ),

        "missing": sorted(
            missing_skills
        )
    }