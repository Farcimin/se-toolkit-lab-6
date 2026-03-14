# Agent

## Overview

`agent.py` is a CLI program that takes a natural-language question, sends it to an LLM, and returns a structured JSON answer.

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
uv run agent.py "What does REST stand for?"
```

**Output** — a single JSON line to stdout:

```json
{"answer": "Representational State Transfer.", "tool_calls": []}
```

## Architecture

```
User question (argv) → agent.py → LLM chat completions API → JSON to stdout
```

1. Loads credentials from `.env.agent.secret`.
2. Sends the question to the LLM with a minimal system prompt.
3. Prints the result as JSON with `answer` and `tool_calls` fields.
4. All debug/progress output goes to stderr.
