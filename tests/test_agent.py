"""Regression test for agent.py — verifies JSON output structure."""

import json
import subprocess
import sys


def test_agent_returns_valid_json_with_required_fields():
    result = subprocess.run(
        [sys.executable, "agent.py", "What is 2+2?"],
        capture_output=True,
        text=True,
        timeout=60,
    )

    assert result.returncode == 0, f"agent.py exited with code {result.returncode}: {result.stderr}"

    data = json.loads(result.stdout)
    assert "answer" in data, "Missing 'answer' field in output"
    assert "tool_calls" in data, "Missing 'tool_calls' field in output"
    assert isinstance(data["answer"], str), "'answer' must be a string"
    assert len(data["answer"]) > 0, "'answer' must not be empty"
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"
