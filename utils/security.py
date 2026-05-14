from passlib.hash import bcrypt

def create_hash(password : str) -> str:
    return bcrypt.hash(password)

def verify_password(password: str, stored_hash:str) -> bool:
    return bcrypt.verify(password, stored_hash)