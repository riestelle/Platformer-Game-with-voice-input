import json, os, time

SCORE_FILE = os.path.join(os.path.dirname(__file__), "scores.json")
BACKUP_FILE = SCORE_FILE + ".bak"


def _load_scores():
    """Load JSON safely or return an empty dict."""
    if not os.path.exists(SCORE_FILE):
        return {}
    try:
        with open(SCORE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("[score_manager] Warning: scores.json corrupted, using empty data.")
        return {}


def _save_scores(scores):
    """Write JSON safely with backup."""
    try:
        with open(BACKUP_FILE, "w", encoding="utf-8") as f:
            json.dump(scores, f, indent=4)
        os.replace(BACKUP_FILE, SCORE_FILE)
    except Exception as e:
        print("[score_manager] Error saving scores:", e)


def save_score(username: str, score: int):
    """Update the user's best score and save history with timestamps."""
    if not username:
        return
    scores = _load_scores()
    user_data = scores.get(username, {"best": 0, "history": []})

    # Append to history
    user_data["history"].append({
        "score": score,
        "time": time.strftime("%Y-%m-%d %H:%M:%S")
    })

    # Update best if higher
    if score > user_data["best"]:
        user_data["best"] = score

    scores[username] = user_data
    _save_scores(scores)


def get_score(username: str):
    """Return only the best numeric score for the user."""
    if not username:
        return 0
    scores = _load_scores()
    user_data = scores.get(username)
    if isinstance(user_data, dict):
        return user_data.get("best", 0)
    elif isinstance(user_data, int):
        return user_data
    return 0


def get_highest_score():
    """Return (username, best_score) of the top player."""
    scores = _load_scores()
    best_user, best_val = None, 0
    for user, data in scores.items():
        if isinstance(data, dict):
            best = data.get("best", 0)
        else:
            best = data
        if best > best_val:
            best_val = best
            best_user = user
    return best_user, best_val


def debug_print():
    """Print full score data (for debugging only)."""
    scores = _load_scores()
    print(json.dumps(scores, indent=4))
