import hashlib
from utils.file_utils import load_json, save_json
USER_FILE = "data/users.json"
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()
def register_user(email, password):
    users = load_json(USER_FILE)
    for user in users:
        if user["email"] == email:
            return False
    users.append({
        "email": email,
        "password": hash_password(password)
    })
    save_json(USER_FILE, users)
    return True
def login_user(email, password):
    users = load_json(USER_FILE)
    hashed = hash_password(password)
    for user in users:
        if user["email"] == email and user["password"] == hashed:
            return True
    return False