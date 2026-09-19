# ============================================================
# SKILLMATCH AI - INTERVIEW QUESTION GENERATOR
# ============================================================

QUESTION_DATABASE = {

    "python": [
        "What are the main features of Python?",
        "What is the difference between a list and a tuple in Python?",
        "Explain exception handling in Python."
    ],

    "aws": [
        "What is AWS and why is it used?",
        "What is the difference between an AWS Region and Availability Zone?",
        "How would you design a basic application on AWS?"
    ],

    "ec2": [
        "What is Amazon EC2?",
        "What is the difference between an EC2 instance and a physical server?",
        "How can you secure an EC2 instance?"
    ],

    "s3": [
        "What is Amazon S3?",
        "What is the difference between an S3 bucket and an object?",
        "How can you control access to an S3 bucket?"
    ],

    "lambda": [
        "What is AWS Lambda?",
        "What are the advantages of serverless computing?",
        "When would you choose Lambda instead of EC2?"
    ],

    "sql": [
        "What is SQL?",
        "What is the difference between WHERE and HAVING?",
        "What is a primary key?"
    ],

    "docker": [
        "What is Docker?",
        "What is the difference between a Docker image and container?",
        "Why is Docker useful in application deployment?"
    ],

    "terraform": [
        "What is Terraform?",
        "What is Infrastructure as Code?",
        "What are the advantages of using Terraform?"
    ],

    "git": [
        "What is Git?",
        "What is the difference between Git and GitHub?",
        "What is a Git branch?"
    ],

    "machine learning": [
        "What is Machine Learning?",
        "What is the difference between supervised and unsupervised learning?",
        "What is overfitting?"
    ],

    "java": [
        "What are the main features of Java?",
        "What is the difference between JDK, JRE and JVM?",
        "What is inheritance in Java?"
    ],

    "javascript": [
        "What is JavaScript?",
        "What is the difference between var, let and const?",
        "What is a JavaScript function?"
    ],

    "react": [
        "What is React?",
        "What is a React component?",
        "What is the difference between state and props?"
    ],

    "mongodb": [
        "What is MongoDB?",
        "What is a document in MongoDB?",
        "How is MongoDB different from a relational database?"
    ]
}


def generate_interview_questions(
    required_skills,
    missing_skills
):

    questions = []

    # First generate questions for missing skills
    for skill in missing_skills:

        skill_lower = skill.lower()

        if skill_lower in QUESTION_DATABASE:

            for question in QUESTION_DATABASE[skill_lower]:

                questions.append({
                    "skill": skill,
                    "question": question
                })

    # Then add questions for required skills
    if len(questions) < 6:

        for skill in required_skills:

            skill_lower = skill.lower()

            if skill_lower in QUESTION_DATABASE:

                for question in QUESTION_DATABASE[skill_lower]:

                    questions.append({
                        "skill": skill,
                        "question": question
                    })

    # Remove duplicate questions
    unique_questions = []

    seen = set()

    for item in questions:

        if item["question"] not in seen:

            unique_questions.append(item)

            seen.add(item["question"])

    # Limit questions
    return unique_questions[:10]