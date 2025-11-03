import os
# --- Preferences and UI flags (TXT version) ---
PREFS_PATH = "prefs.txt"

def load_prefs_txt():
    prefs = {
        "show_tutorial": True,
        "show_quick_tips": True
    }
    try:
        if os.path.exists(PREFS_PATH):
            with open(PREFS_PATH, "r") as f:
                for line in f:
                    if "=" in line:
                        key, val = line.strip().split("=", 1)
                        prefs[key] = val.lower() == "true"
    except Exception as e:
        print(f"[prefs] Failed to load prefs.txt: {e}")
    return prefs

def save_prefs_txt(prefs):
    try:
        with open(PREFS_PATH, "w") as f:
            for key, val in prefs.items():
                f.write(f"{key}={str(val)}\n")
    except Exception as e:
        print(f"[prefs] Failed to save prefs.txt: {e}")