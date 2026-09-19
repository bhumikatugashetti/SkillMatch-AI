import re


SKILLS_DATABASE = [

    # Programming
    "Python",
    "Java",
    "C",
    "C++",
    "JavaScript",

    # Web
    "HTML",
    "CSS",
    "React",
    "Flask",
    "Django",
    "Node.js",

    # Database
    "SQL",
    "MySQL",
    "PostgreSQL",
    "MongoDB",

    # Cloud
    "AWS",
    "EC2",
    "S3",
    "Lambda",
    "DynamoDB",
    "IAM",
    "CloudWatch",
    "Azure",
    "Google Cloud",

    # DevOps
    "Git",
    "GitHub",
    "Docker",
    "Kubernetes",
    "Terraform",
    "CI/CD",
    "Jenkins",
    "Linux",

    # Data / AI
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "NLP",
    "Computer Vision",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "Power BI",
    "Excel",

    # Other
    "Data Analysis",
    "Data Science",
    "Cybersecurity"
]


def extract_skills(text):

    detected_skills = []

    for skill in SKILLS_DATABASE:

        pattern = (
            r"(?<![A-Za-z0-9])"
            + re.escape(skill)
            + r"(?![A-Za-z0-9])"
        )

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):

            detected_skills.append(skill)

    return detected_skills