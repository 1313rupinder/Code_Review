import re

SECRET_ASSIGNMENT = re.compile(
    r"""(?i)\b[\w-]*(?:password|passwd|pwd|secret|token|api[_-]?key|credential|private[_-]?key)[\w-]*["']?[ \t]*[:=][ \t]*(["'])(.+?)\1"""
)
KNOWN_TOKEN = re.compile(
    r"\b(?:gsk_[A-Za-z0-9]{10,}|ghp_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}"
    r"|sk-[A-Za-z0-9_-]{16,}|AKIA[0-9A-Z]{16}|xox[baprs]-[A-Za-z0-9-]{10,})"
)
MIN_SECRET_LENGTH = 4

def _hide_value(match):
    value = match.group(2)
    if len(value) < MIN_SECRET_LENGTH:
        return match.group(0)
    return match.group(0).replace(value, "<redacted>")

def redact_secret_like(text):
    text = SECRET_ASSIGNMENT.sub(_hide_value, text)
    return KNOWN_TOKEN.sub("<redacted>", text)