from rag import search_knowledge


query = "brute force login"


results = search_knowledge(query)


print("\nRAG Search Results:\n")


for result in results:

    print("File:", result["filename"])
    print("Score:", result["score"])
    print()
    print(result["text"])
    print("----------------------")