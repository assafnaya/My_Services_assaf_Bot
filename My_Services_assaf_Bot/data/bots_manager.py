import json
import os
import uuid

BOTS_DIR = "data/bots"
INDEX_FILE = "data/bots.json"

def load_index():
    if not os.path.exists(INDEX_FILE):
        return {}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_index(data):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def create_bot(name, token, owner_id):
    bots = load_index()
    bot_id = uuid.uuid4().hex[:8]

    bot_data = {
        "id": bot_id,
        "name": name,
        "token": token,
        "owner": owner_id,
        "channels": {},
        "scripts": []
    }

    with open(f"{BOTS_DIR}/{bot_id}.json", "w", encoding="utf-8") as f:
        json.dump(bot_data, f, indent=2, ensure_ascii=False)

    bots[bot_id] = name
    save_index(bots)
    return bot_id

def list_bots():
    return load_index()

