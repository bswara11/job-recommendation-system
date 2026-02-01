import numpy as np

def top_matching_keywords(resume_text, job_text, top_n=5):
    vectorizer = TfidfVectorizer()
    tfidf = vectorizer.fit_transform([resume_text, job_text])

    feature_names = np.array(vectorizer.get_feature_names_out())

    resume_vec = tfidf[0].toarray().flatten()
    job_vec = tfidf[1].toarray().flatten()

    # shared importance = product
    shared_score = resume_vec * job_vec

    if shared_score.sum() == 0:
        return []

    top_indices = shared_score.argsort()[-top_n:][::-1]
    return feature_names[top_indices].tolist()
