
def noteEntity(item) -> dict:
    return{
        "id": str(item["_id"]),
        "title": item.get("title",""),
        "desc": item.get("desc",""),
        "important": item.get("important", False),
        "created_at": item.get("created_at")
    }

def notesEntity(items) -> list:
    return [noteEntity(item) for item in items]