import os


KNOWLEDGE_FOLDER = "knowledge"


def load_knowledge():

    documents = []

    for filename in os.listdir(KNOWLEDGE_FOLDER):

        if filename.endswith(".txt"):

            path = os.path.join(
                KNOWLEDGE_FOLDER,
                filename
            )

            with open(path, "r") as file:
                text = file.read()

            documents.append({
                "filename": filename,
                "text": text
            })

    return documents


def search_knowledge(query):

    documents = load_knowledge()

    results = []

    query_words = query.lower().split()

    for document in documents:

        text = document["text"].lower()

        score = 0

        for word in query_words:

            if word in text:
                score += 1

        if score > 0:

            results.append({
                "filename": document["filename"],
                "text": document["text"],
                "score": score
            })

    results.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return results