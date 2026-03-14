# Task 2 — The Documentation Agent

## Tool schemas

Define `read_file` and `list_files` as OpenAI-compatible function-calling tool schemas passed in the `tools` parameter of the chat completion request.

- `read_file`: takes `path` (string), returns file contents.
- `list_files`: takes `path` (string), returns newline-separated directory listing.

## Agentic loop

1. Send question + tool definitions to the LLM.
2. If response contains `tool_calls` → execute each tool, append results as `tool` role messages, loop back.
3. If response is plain text → extract answer, output JSON, exit.
4. Cap at 10 tool calls to prevent infinite loops.

## Path security

Both tools resolve the path relative to the project root and reject any path that escapes it (e.g., `../`). Use `os.path.realpath` to resolve symlinks and verify the resolved path starts with the project root.

## System prompt strategy

Instruct the LLM to first use `list_files` to discover available wiki files, then `read_file` to read relevant files and find the answer. The LLM should include a `source` reference (file path + section anchor) in its final answer.

## Output format

Add `source` field to the JSON output. Populate `tool_calls` array with `{tool, args, result}` entries for each tool call made during the loop.
