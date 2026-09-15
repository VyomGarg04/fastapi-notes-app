from utils.semantic_search import semantic_search

results = semantic_search(
    "how can I efficiently search a sorted array?",
    "6a7ee2f2fb619497699a95cd"
)

for result in results:
    print(result["title"], "→", result["score"])