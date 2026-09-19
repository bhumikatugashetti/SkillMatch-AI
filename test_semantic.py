from services.semantic_matcher import calculate_semantic_similarity


candidate_skills = [
    "Python",
    "Amazon Web Services",
    "Machine Learning",
    "SQL"
]

required_skills = [
    "Python",
    "AWS",
    "Machine Learning",
    "SQL"
]


score = calculate_semantic_similarity(
    candidate_skills,
    required_skills
)


print("AI Semantic Similarity Score:")
print(score, "%")