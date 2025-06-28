import json
import os
import re
def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)
def save_json(filepath, data):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
def sanitize_filename(name):
    name = re.sub(r'[\\/*?:"<>|]', '', name)
    return name.strip().replace(" ", "_")
def save_chat(user_email, chat_id, messages):
    user_dir = f"data/chats/{sanitize_filename(user_email)}"
    os.makedirs(user_dir, exist_ok=True)
    file_path = os.path.join(user_dir, f"{sanitize_filename(chat_id)}.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)
def load_chat(user_email, chat_id):
    file_path = f"data/chats/{sanitize_filename(user_email)}/{sanitize_filename(chat_id)}.json"
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []
def list_chats(user_email):
    user_dir = f"data/chats/{sanitize_filename(user_email)}"
    if not os.path.exists(user_dir):
        return []
    return sorted([f.replace(".json", "") for f in os.listdir(user_dir) if f.endswith(".json")])
def get_unique_chat_id(user_email, base_name):
    user_dir = f"data/chats/{sanitize_filename(user_email)}"
    os.makedirs(user_dir, exist_ok=True)
    base_name = sanitize_filename(base_name)
    chat_id = base_name
    i = 1
    while os.path.exists(os.path.join(user_dir, f"{chat_id}.json")):
        chat_id = f"{base_name}_{i}"
        i += 1
    return chat_id