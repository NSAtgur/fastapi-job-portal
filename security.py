from passlib.hash import argon2

def generate_password_hash(password:str)->str:
    return argon2.hash(password)

def verify_password_hash(password:str, hashed:str)->bool:
    return argon2.verify(password, hashed)
