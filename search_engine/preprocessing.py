import re
from nltk.stem import PorterStemmer


# ---------------------------------
# STEMMER OBJECT
# ---------------------------------
stemmer = PorterStemmer()


# ---------------------------------
# STOPWORDS LIST
# ---------------------------------
STOPWORDS = {
    "the", "is", "and", "of", "in", "to",
    "a", "for", "on", "with", "that",
    "this", "it", "as", "are", "was",
    "at", "by", "an", "be", "from"
}


def preprocess_text(text, remove_stopwords=True):
    """
    Preprocess text by:
    1. Lowercasing
    2. Removing punctuation
    3. Tokenizing
    4. Optional stopword removal
    5. Stemming
    """

    # 1️⃣ Convert to lowercase
    text = text.lower()

    # 2️⃣ Remove punctuation
    text = re.sub(r'[^a-z0-9_\s]', '', text)

    # 3️⃣ Tokenization
    tokens = text.split()

    # 4️⃣ Optional Stopword Removal
    if remove_stopwords:
        tokens = [
            word for word in tokens
            if word not in STOPWORDS
        ]

    # 5️⃣ Stemming
    tokens = [
        stemmer.stem(word)
        for word in tokens
    ]

    return tokens


if __name__ == "__main__":

    sample_text = "The systems are searching and searched properly"

    print("With stopword removal:")
    print(preprocess_text(sample_text, remove_stopwords=True))

    print("\nWithout stopword removal:")
    print(preprocess_text(sample_text, remove_stopwords=False))