import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st


@st.cache_data(ttl=3600, show_spinner=False)
def recommend_by_similarity(user_papers, embeddings, embedding_columns, n=10):
    """

    Args:
        user_papers: list of paper_id that user read
        embeddings: list of paper embeddings
        embedding_columns: list of name of embedding columns
        n: the number of recommended paper returned

    Returns: list of recommended papers id

    """
    user_embeddings = []
    for paper in user_papers:
        user_embeddings.append(embeddings.loc[embeddings["id"] == paper][embedding_columns])
    user_embeddings = np.concatenate(user_embeddings)

    similarity = cosine_similarity(embeddings[embedding_columns], user_embeddings)
    s_similarity = np.mean(similarity, axis=1)
    top_10_indices = s_similarity.argsort()[-n:][::-1]
    top_similarities = s_similarity[top_10_indices]
    return embeddings.iloc[top_10_indices, 0], top_similarities
