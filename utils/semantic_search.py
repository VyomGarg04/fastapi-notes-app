from config.db import conn
from utils.embedding import generate_embedding

notes_collection = conn.notes.notes

def semantic_search(query: str, user_id: str, limit: int = 10):
    query_vector = generate_embedding(query)
    vector_search_stage = {
        "$vectorSearch": {
            "index": "note_embedding_index",
            "path": "embedding",
            "queryVector": query_vector,
            "numCandidates": 50,
            "limit": limit,
            "filter": {
                "user_id": user_id
            },
        }
    }
    results = notes_collection.aggregate([
    vector_search_stage,
    {
        "$project": {
            "title": 1,
            "content": 1,
            "score": {
                "$meta": "vectorSearchScore"
            }
        }
    }
])
    return list(results)
