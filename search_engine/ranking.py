from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def rank_results(query, documents):
    """
    query = search text
    documents = dict {filename: content}
    """

    filenames = list(documents.keys())
    texts = list(documents.values())

    if not texts:
        return []

    vectorizer = TfidfVectorizer()

    tfidf_matrix = vectorizer.fit_transform(texts + [query])

    similarity = cosine_similarity(
        tfidf_matrix[-1],
        tfidf_matrix[:-1]
    ).flatten()

    ranked = sorted(
        zip(filenames, similarity),
        key=lambda x: x[1],
        reverse=True
    )

    return ranked