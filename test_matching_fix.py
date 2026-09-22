import sys
import os

# Ensure project root is in python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from services.job_matcher import calculate_match, normalize_skills
from services.interview_generator import generate_interview_questions

def run_test():
    candidate_skills = [
        "Python", "JavaScript", "HTML", "CSS", "SQL", "EC2",
        "Lambda", "DynamoDB", "IAM", "Git", "GitHub", "CI/CD"
    ]

    job_required_skills = [
        "Python", "SQL", "AWS", "EC2", "S3", "Lambda",
        "Git", "Docker", "Terraform"
    ]

    resume_text = "Experienced developer proficient in Python, JavaScript, HTML, CSS, SQL, EC2, Lambda, DynamoDB, IAM, Git, GitHub, and CI/CD pipelines."
    job_description = "Looking for a Cloud DevOps Engineer skilled in Python, SQL, AWS, EC2, S3, Lambda, Git, Docker, and Terraform."

    # Test match calculation
    result = calculate_match(
        candidate_skills=candidate_skills,
        required_skills=job_required_skills,
        resume_text=resume_text,
        job_description=job_description
    )

    print("=== CANDIDATE MATCH RESULT ===")
    print("Hybrid Score:", result["score"])
    print("Keyword Match Score:", result["keyword_score"])
    print("Semantic AI Score:", result["semantic_score"])
    print("Matched Skills:", result["matched"])
    print("Skill Gaps (Missing):", result["missing"])

    # Test interview questions generation
    questions = generate_interview_questions(
        required_skills=job_required_skills,
        missing_skills=result["missing"]
    )

    print("\n=== GENERATED INTERVIEW QUESTIONS ===")
    for idx, q in enumerate(questions, 1):
        print(f"{idx}. [{q['skill']}] {q['question']}")

    # Assertions
    expected_matched = {"Python", "SQL", "EC2", "Lambda", "Git"}
    expected_missing = {"AWS", "S3", "Docker", "Terraform"}

    assert expected_matched.issubset(set(result["matched"])), f"Expected matched skills subset failed: {result['matched']}"
    assert expected_missing.issubset(set(result["missing"])), f"Expected missing skills subset failed: {result['missing']}"
    assert result["keyword_score"] > 0, "Keyword score should be greater than 0%"
    assert len(questions) > 0, "Interview questions should be generated for missing skills"

    print("\n[SUCCESS] REGRESSION TEST PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_test()
