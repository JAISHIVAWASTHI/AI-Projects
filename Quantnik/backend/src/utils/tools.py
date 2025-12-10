import os, json, re
from datetime import datetime


def save_text_to_file(text: str, file_path: str = None) -> str:
    """
    Saves text to a .txt file.
    """
    try:
        if not file_path:
            folder = "new_text"
            os.makedirs(folder, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_path = os.path.join(folder, f"text_{timestamp}.txt")

        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            f.write(text.strip())

        print(f"Text saved successfully: {file_path}")
        return file_path

    except Exception as e:
        print(f"Error saving Text file: {e}")
        return ""


def read_text_to_file(file_path: str = None) -> str:
    """
    Read text file.
    """

    try:
        if not file_path:
            return None

        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    except Exception as e:
        print(f"Error in Reading Text file: {e}")
        return None


def save_dict_json(file_path, data_dict):
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data_dict, f, indent=4)
        return True, "File saved successfully"
    except Exception as e:
        return False, f"Error saving JSON: {str(e)}"


# ---------------------------
# Load Dictionary from JSON
# ---------------------------
def load_dict_json(file_path):
    try:
        if not os.path.exists(file_path):
            return None, "File not found"

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return True, data
    except json.JSONDecodeError:
        return None, "Invalid JSON format"
    except Exception as e:
        return None, f"Error loading JSON: {str(e)}"


def convert_to_project_key(text: str) -> str:
    """
    Convert any input into a valid uppercase Jira project key format.
    Example:
        "my project 123" -> "MPROJECT123"
        "123abc" -> "P123ABC"
    """

    # Remove all characters except letters and numbers
    cleaned = re.sub(r"[^A-Za-z0-9]", "", text)

    # Convert to uppercase
    cleaned = cleaned.upper()

    # If empty after cleaning, return default
    if cleaned == "":
        return "P"

    # Ensure first character is a letter
    if not cleaned[0].isalpha():
        cleaned = "P" + cleaned

    return cleaned