import os
from dotenv import load_dotenv

# Load .env from the same directory as this file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), ".env"))

ALLOWED_EXTENSIONS = {
    ".py", ".java", ".cpp", ".c", ".js", ".ts", ".html", ".css", ".sql"
}

IGNORED_DIRECTORIES = {
    ".git", "__pycache__", "node_modules", ".venv", "venv", "dist", "build"
}

# Loaded from .env → GEMINI_MODEL, falls back to gemini-2.0-flash
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")

# Max characters per file sent to LLM (token budget)
MAX_FILE_CHARS = 8000

# Max total files sent to LLM per review
MAX_FILES = 30
