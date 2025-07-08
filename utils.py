import os
import json

def save_feedback(user, movie, liked):
    if not user:
        return
    feedback_path = "data/user_feedback.json"
    os.makedirs(os.path.dirname(feedback_path), exist_ok=True)
    feedback = {}
    if os.path.exists(feedback_path):
        with open(feedback_path, "r", encoding="utf-8") as f:
            try:
                feedback = json.load(f)
            except json.JSONDecodeError:
                feedback = {}
    if user not in feedback:
        feedback[user] = {}
    feedback[user][movie] = liked
    with open(feedback_path, "w", encoding="utf-8") as f:
        json.dump(feedback, f, indent=4, ensure_ascii=False)
