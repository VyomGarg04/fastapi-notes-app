
def noteEntity(item) -> dict:
    return{
        "id": str(item["_id"]),
        "title": item.get("title",""),
        "content": item.get("content",""),
        "important": item.get("important", False),
        "category": item.get("category"),
        "tags": item.get("tags", []),
        "created_at": item.get("created_at"),
        "updated_at": item.get("updated_at"),
    }

def notesEntity(items) -> list:
    return [noteEntity(item) for item in items]