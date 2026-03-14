# Agent

## Overview

`agent.py` is a CLI agent that takes a natural-language question, uses tools to explore the project wiki, and returns a structured JSON answer grounded in the documentation.

## LLM provider

Qwen Code API (`qwen3-coder-plus`) accessed through an OpenAI-compatible chat completions endpoint deployed on the VM.

## Configuration

Copy the example env file and fill in your credentials:

```bash
cp .env.agent.example .env.agent.secret
```

Required variables in `.env.agent.secret`:

| Variable       | Description                          |
| -------------- | ------------------------------------ |
| `LLM_API_KEY`  | API key for the LLM provider         |
| `LLM_API_BASE` | Base URL of the OpenAI-compatible API |
| `LLM_MODEL`    | Model name (default: `qwen3-coder-plus`) |

## Usage

```bash
uv run agent.py "How do you resolve a merge conflict?"
```

**Output** — a single JSON line to stdout:

```json
{
  "answer": "Edit the conflicting file, choose which changes to keep, then stage and commit.",
  "source": "wiki/git-workflow.md#resolving-merge-conflicts",
  "tool_calls": [
    {"tool": "list_files", "args": {"path": "wiki"}, "result": "..."},
    {"tool": "read_file", "args": {"path": "wiki/git-workflow.md"}, "result": "..."}
  ]
}
```

## Tools

### `read_file`

Reads a file from the project repository. Takes a relative `path` from the project root. Returns file contents or an error message. Rejects paths that traverse outside the project directory.

### `list_files`

Lists files and directories at a given path. Takes a relative directory `path`. Returns a newline-separated listing. Rejects paths outside the project directory.

## Agentic loop

1. Send the user's question and tool definitions to the LLM.
2. If the LLM responds with `tool_calls` → execute each tool, append results as `tool` messages, loop back.
3. If the LLM responds with plain text → that is the final answer. Output JSON and exit.
4. Maximum of 10 tool calls per question to prevent infinite loops.

## System prompt strategy

The system prompt instructs the LLM to:

1. Use `list_files` on the `wiki` directory to discover available files.
2. Use `read_file` on the most relevant file(s) to find the answer.
3. Include a source reference (`file_path#section-anchor`) in the response.

## Architecture

```
User question (argv)
       │
       ▼
   agent.py ◄──── .env.agent.secret
       │
       ▼
   LLM API (chat completions + tools)
       │
       ├── tool_calls? ──yes──▶ execute tool ──▶ back to LLM
       │
       no
       │
       ▼
   JSON output (stdout)
```
