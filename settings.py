SEVERITY_RANK = {"high": 3, "medium": 2, "low": 1}
MIN_SEVERITY = "low"
MAX_COMMENTS = 10
MAX_MODEL_CALLS = 25

SKIP_RULES = {"B403", "B404"}
SECRET_RULES = {"B105", "B106", "B107"}
SKIP_DIRS = {".git", "Hii", "venv", ".venv", "__pycache__", ".ruff_cache", "node_modules"}

MODEL = "openai/gpt-oss-120b"