from review_finding import get_secret_values, redact
from build_prompt import get_code_context

secrets = get_secret_values("samples/app.py", 3, 3)
print("secrets found:", secrets)
print(redact("Possible hardcoded password: 'admin123'", secrets))
print(redact(get_code_context("samples/app.py", 3, 3), secrets))