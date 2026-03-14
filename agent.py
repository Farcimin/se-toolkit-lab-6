"""CLI agent that sends a question to an LLM and returns a JSON answer."""

import json
import os
import sys
from pathlib import Path

import httpx
from dotenv import load_dotenv

load_dotenv(".env.agent.secret")

API_KEY = os.environ.get("LLM_API_KEY", "")
API_BASE = os.environ.get("LLM_API_BASE", "").rstrip("/")
MODEL = os.environ.get("LLM_MODEL", "qwen3-coder-plus")

PROJECT_ROOT = Path(__file__).resolve().parent

MAX_TOOL_CALLS = 10

SYSTEM_PROMPT = """\
You are a documentation agent for a software project. \
Answer the user's question using the project's wiki files.

Steps:
1. Call list_files with path "wiki" to see available wiki files.
2. Based on the file names, call read_file on the most relevant file(s).
3. Find the answer in the file content and respond with:
   - Your answer to the question.
   - A source reference in the format: file_path#section-anchor \
(e.g., wiki/git-workflow.md#resolving-merge-conflicts).

Always ground your answer in the wiki content. Be concise.\
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read a file from the project repository.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative path from project root.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files and directories at a given path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Relative directory path from project root.",
                    }
                },
                "required": ["path"],
            },
        },
    },
]


def _safe_resolve(path_str: str) -> Path | None:
    """Resolve a relative path safely, rejecting traversal outside the project."""
    resolved = (PROJECT_ROOT / path_str).resolve()
    if not str(resolved).startswith(str(PROJECT_ROOT)):
        return None
    return resolved


def tool_read_file(path: str) -> str:
    resolved = _safe_resolve(path)
    if resolved is None:
        return "Error: path traversal outside project directory is not allowed."
    if not resolved.is_file():
        return f"Error: file not found: {path}"
    return resolved.read_text(encoding="utf-8")


def tool_list_files(path: str) -> str:
    resolved = _safe_resolve(path)
    if resolved is None:
        return "Error: path traversal outside project directory is not allowed."
    if not resolved.is_dir():
        return f"Error: directory not found: {path}"
    entries = sorted(e.name for e in resolved.iterdir() if not e.name.startswith("."))
    return "\n".join(entries)


TOOL_DISPATCH = {
    "read_file": tool_read_file,
    "list_files": tool_list_files,
}


def call_llm(messages: list[dict]) -> dict:
    response = httpx.post(
        f"{API_BASE}/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}"},
        json={
            "model": MODEL,
            "messages": messages,
            "tools": TOOLS,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run agent.py <question>", file=sys.stderr)
        sys.exit(1)

    question = sys.argv[1]

    if not API_KEY or not API_BASE:
        print("Error: LLM_API_KEY and LLM_API_BASE must be set in .env.agent.secret", file=sys.stderr)
        sys.exit(1)

    messages: list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]

    tool_call_log: list[dict] = []
    total_tool_calls = 0

    while True:
        print(f"Calling {MODEL}... (tool calls so far: {total_tool_calls})", file=sys.stderr)
        data = call_llm(messages)
        choice = data["choices"][0]
        message = choice["message"]

        # Add assistant message to conversation
        messages.append(message)

        # Check if the LLM wants to call tools
        if message.get("tool_calls") and total_tool_calls < MAX_TOOL_CALLS:
            for tc in message["tool_calls"]:
                func_name = tc["function"]["name"]
                func_args = json.loads(tc["function"]["arguments"])
                tool_call_id = tc["id"]

                print(f"  Tool: {func_name}({func_args})", file=sys.stderr)

                handler = TOOL_DISPATCH.get(func_name)
                if handler is None:
                    result_str = f"Error: unknown tool: {func_name}"
                else:
                    result_str = handler(**func_args)

                tool_call_log.append({
                    "tool": func_name,
                    "args": func_args,
                    "result": result_str[:500],  # truncate for output
                })

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_id,
                    "content": result_str,
                })

                total_tool_calls += 1
                if total_tool_calls >= MAX_TOOL_CALLS:
                    print("  Max tool calls reached.", file=sys.stderr)
                    break
        else:
            # Final text answer
            answer_text = message.get("content", "")
            break

    # Extract source from the answer if the LLM included it
    source = ""
    for log_entry in tool_call_log:
        if log_entry["tool"] == "read_file":
            source = log_entry["args"].get("path", "")
            break

    result = {
        "answer": answer_text,
        "source": source,
        "tool_calls": tool_call_log,
    }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
