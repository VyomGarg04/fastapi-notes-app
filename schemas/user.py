# schema output
def userEntity(item) -> dict:
    return{
        "id": str(item["_id"]),
        "username": item.get("username",""),
        "email": item.get("email",""),
    }

def usersEntity(items) -> list:
    return [userEntity(item) for item in items]