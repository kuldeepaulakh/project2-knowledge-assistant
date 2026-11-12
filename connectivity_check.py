import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv(Path(__file__).resolve().parent / ".env")
model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")
if not os.getenv("GROQ_API_KEY"):
    raise SystemExit("BLOCKED: GROQ_API_KEY is not configured in local .env (key not printed).")
result = Groq(api_key=os.environ["GROQ_API_KEY"]).chat.completions.create(
    model=model, temperature=0, messages=[{"role": "user", "content": "Reply with READY only"}]
)
print({"provider": "Groq", "model": model, "response": result.choices[0].message.content})

