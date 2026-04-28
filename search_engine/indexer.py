# import os
# from collections import defaultdict
# from .preprocessing import preprocess_text


# def build_inverted_index(upload_folder):

#     inverted_index = defaultdict(dict)

#     for filename in os.listdir(upload_folder):

#         filepath = os.path.join(upload_folder, filename)

#         with open(filepath, 'r', encoding='utf-8') as file:
#             text = file.read()

#         tokens = preprocess_text(text)

#         for word in tokens:

#             if filename not in inverted_index[word]:
#                 inverted_index[word][filename] = 0

#             inverted_index[word][filename] += 1

#     return inverted_index


# if __name__ == "__main__":

#     upload_folder = os.path.join(
#         os.path.dirname(os.path.dirname(__file__)),
#         "uploads"
#     )

#     print("Files found:", os.listdir(upload_folder))

#     index = build_inverted_index(upload_folder)

#     print(index)





import os
import PyPDF2
from collections import defaultdict
from .preprocessing import preprocess_text


def build_inverted_index(upload_folder):

    inverted_index = defaultdict(dict)

    for filename in os.listdir(upload_folder):

        filepath = os.path.join(upload_folder, filename)

        if os.path.isdir(filepath):
            continue

        text = ""

        if filename.lower().endswith(".txt"):

            with open(filepath, "r", encoding="utf-8") as file:
                text = file.read()

        elif filename.lower().endswith(".pdf"):

            with open(filepath, "rb") as file:
                reader = PyPDF2.PdfReader(file)

                for page in reader.pages:
                    extracted = page.extract_text()

                    if extracted:
                        text += extracted

        else:
            continue

        tokens = preprocess_text(text)

        for word in tokens:

            if filename not in inverted_index[word]:
                inverted_index[word][filename] = 0

            inverted_index[word][filename] += 1

    return inverted_index


if __name__ == "__main__":

    upload_folder = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "uploads"
    )

    print("Files found:", os.listdir(upload_folder))

    index = build_inverted_index(upload_folder)

    print(index)



