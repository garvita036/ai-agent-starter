# tools/file_tool.py
import os

def run(path: str) -> str:
    path = path.strip()
    if not path:
        return "No file path provided."
    # Basic safety: only allow reading from the repo subtree
    safe_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    requested = os.path.abspath(path)
    if not requested.startswith(safe_root):
        return f"Refusing to read outside project directory: {path}"

    if not os.path.exists(requested):
        return f"File not found: {path}"

    # If it's an image, inform user (no OCR)
    ext = os.path.splitext(requested)[1].lower()
    if ext in [".png", ".jpg", ".jpeg", ".gif"]:
        return f"Image file detected at {path}. (This tool does not parse images.)"

    try:
        with open(requested, "r", encoding="utf-8") as f:
            data = f.read(10000)  # limit to first 10k chars
            if len(data) == 0:
                return "File is empty."
            return data
    except Exception as e:
        return f"Error reading file: {e}"
