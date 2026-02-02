import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd

from src.preprocessing import clean_text
from src.resume_parser import extract_text_from_pdf
from src.recommender import compute_similarity
from src.ranking import skill_overlap_score, experience_score
from src.recommender import compute_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# ---------- App Title ----------
st.set_page_config(page_title="Job Recommendation System", layout="wide")
st.title("💼 Intelligent Job & Internship Recommendation System")

st.write(
    "Upload your resume and get personalized job recommendations "
    "based on NLP and machine learning."
)

# ---------- Load Job Data ----------
@st.cache_data
def load_jobs():
    base_dir = os.path.dirname(__file__)
    file_path = os.path.join(
        base_dir, "data", "raw", "clean_jobs.csv"
    )
    df = pd.read_csv(file_path)
    df["clean_description"] = df["description"].apply(clean_text)
    return df

# ---------- Resume Upload ----------
jobs_df = load_jobs()
st.sidebar.header("🔎 Filters")

# Location filter
locations = ["All"] + sorted(jobs_df["location"].dropna().unique().tolist())
selected_location = st.sidebar.selectbox("Location", locations)

# Work type filter
work_types = ["All"] + sorted(jobs_df["work_type"].dropna().unique().tolist())
selected_work_type = st.sidebar.selectbox("Work Type", work_types)

filtered_jobs = jobs_df.copy()

if selected_location != "All":
    filtered_jobs = filtered_jobs[
        filtered_jobs["location"] == selected_location
    ]

if selected_work_type != "All":
    filtered_jobs = filtered_jobs[
        filtered_jobs["work_type"] == selected_work_type
    ]

uploaded_file = st.file_uploader("📄 Upload your resume (PDF)", type=["pdf"])

def explain_recommendation(resume_text, job_text, top_n=5):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([resume_text, job_text])

    feature_names = np.array(vectorizer.get_feature_names_out())
    shared = tfidf[0].toarray().flatten() * tfidf[1].toarray().flatten()

    if shared.sum() == 0:
        return "Matched based on overall relevance"

    top_indices = shared.argsort()[-top_n:][::-1]
    keywords = feature_names[top_indices]

    return ", ".join(keywords)

if uploaded_file:
    # Save temp file
    with open("temp_resume.pdf", "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Extract + clean resume
    raw_text = extract_text_from_pdf("temp_resume.pdf")
    cleaned_resume = clean_text(raw_text)

    st.success("Resume processed successfully!")

    # ---------- Similarity ----------
    similarity_scores = compute_similarity(
        cleaned_resume,
       filtered_jobs["clean_description"].tolist()


    filtered_jobs["similarity_score"] = similarity_scores

    # ---------- Ranking ----------
    final_scores = []
    for _, row in jobs_df.iterrows():
        skill_score = skill_overlap_score(cleaned_resume, row["clean_description"])
        exp_score = experience_score(cleaned_resume)

        final_score = (
            0.6 * row["similarity_score"]
            + 0.3 * skill_score
            + 0.1 * exp_score
        )
        final_scores.append(final_score)

    jobs_df["final_score"] = final_scores

    ranked_jobs = jobs_df.sort_values(by="final_score", ascending=False).head(5)

    # ---------- Display Results ----------
    st.subheader("🔍 Top Job Recommendations")
  st.subheader("🔍 Top Job Recommendations")

for _, job in ranked_jobs.iterrows():
    st.markdown(f"### {job['title']} — {job['company']}")
    st.write(f"📍 Location: {job['location']}")
    st.write(f"🏢 Work Type: {job['work_type']}")
    st.write(f"⭐ Match Score: {job['final_score']:.2f}")

    reason = explain_recommendation(
        cleaned_resume,
        job["clean_description"]
    )

    st.info(f"**Why recommended:** {reason}")
    st.divider()

    
