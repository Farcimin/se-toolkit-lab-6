"""CLI agent that sends a question to an LLM and returns a JSON answer."""

import json
import os
import sys

import httpx
from dotenv import load_dotenv

load_dotenv(".env.agent.secret")

API_KEY = os.environ.get("LLM_API_KEY", "")
API_BASE = os.environ.get("LLM_API_BASE", "").rstrip("/")
MODEL = os.environ.get("LLM_MODEL", "qwen3-coder-plus")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py <question>", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    if not API_KEY or not API_BASE:
        print("Error: LLM_API_KEY and LLM_API_BASE must be set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    print(f"Sending question to {MODEL}...", file=sys.stderr)

    response = httpx.post(
        f"{API_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": MODEL,
            "messages": [
                {"role": "system", "content": "Answer the user's question concisely."},
                {"role": "user", "content": question},
            ],
        },
        timeout=60,
    )
    response.raise_for_status()

    data = response.json()
    answer_text = data["choices"][0]["message"]["content"]

    result = {"answer": answer_text, "tool_calls": []}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
