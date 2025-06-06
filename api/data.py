import json

def load():
    try:
        with open("config.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Lỗi khi load config.json: {e}")
        return {}

def save(data):
    try:
        with open("config.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Lỗi khi lưu config.json: {e}")