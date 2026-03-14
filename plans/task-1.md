# Task 1 — Call an LLM from Code

## LLM provider

Qwen Code API (`qwen3-coder-plus`) deployed on the VM via the OpenAI-compatible proxy. Credentials are stored in `.env.agent.secret`.

## Agent structure

`agent.py` is a single-file CLI script:

1. Load environment variables from `.env.agent.secret` using `python-dotenv`.
2. Read the user's question from `sys.argv[1]`.
3. Send a chat completion request to the LLM via `httpx` (already a project dependency).
4. Extract the assistant's reply from the response JSON.
5. Print `{"answer": "...", "tool_calls": []}` to stdout.

All debug output goes to stderr. The `tool_calls` array is empty for this task and will be populated in Task 2.

## Testing

One regression test runs `agent.py` as a subprocess, parses stdout as JSON, and asserts that `answer` (non-empty string) and `tool_calls` (list) are present.
