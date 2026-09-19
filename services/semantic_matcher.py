# ============================================================
# SKILLMATCH AI - SEMANTIC RESUME-JOB MATCHING
# ============================================================

from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Load AI language model
model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


def calculate_semantic_similarity(
    resume_text,
    job_description
):

    if not resume_text or not job_description:
        return 0


    # Convert resume and job description
    # into AI embeddings
    resume_embedding = model.encode(
        [resume_text]
    )

    job_embedding = model.encode(
        [job_description]
    )


    # Calculate cosine similarity
    similarity = cosine_similarity(
        resume_embedding,
        job_embedding
    )[0][0]


    # Convert similarity into percentage
    score = similarity * 100


    return round(
        score,
        2
    )