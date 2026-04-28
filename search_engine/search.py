import os
from .preprocessing import preprocess_text


def search_documents(query, inverted_index, upload_folder):

    results = {}

    raw_query = query.strip().lower()
    query = query.strip().lower()

    if not inverted_index:
        return {}

    # =====================================
    # 1️⃣ FILENAME SEARCH (FIXED)
    # =====================================
    clean_query = raw_query.replace("_", "").replace(" ", "")

    for filename in os.listdir(upload_folder):

        name_without_ext = filename.lower().replace(".txt", "")
        clean_name = name_without_ext.replace("_", "").replace(" ", "")

        if clean_query in clean_name:
            if filename not in results:
                results[filename] = 0

    # =====================================
    # 2️⃣ PHRASE SEARCH
    # =====================================
    if query.startswith('"') and query.endswith('"'):

        phrase = query[1:-1].lower()

        for filename in os.listdir(upload_folder):

            filepath = os.path.join(upload_folder, filename)

            if not os.path.exists(filepath):
                continue

            with open(filepath, "r", encoding="utf-8") as file:
                content = file.read().lower()

            if phrase in content:
                results[filename] = results.get(filename, 0) + content.count(phrase)

        return results

    # =====================================
    # 3️⃣ KEYWORD SEARCH
    # =====================================
    query_tokens = preprocess_text(query)

    for word in query_tokens:

        if word in inverted_index:

            for file, freq in inverted_index[word].items():
                results[file] = results.get(file, 0) + freq

    return results