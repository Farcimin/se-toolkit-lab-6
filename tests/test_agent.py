"""Regression tests for agent.py."""

import json
import subprocess
import sys


def _run_agent(question: str) -> dict:
    result = subprocess.run(
        [sys.executable, "agent.py", question],
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert result.returncode == 0, f"agent.py exited with code {result.returncode}: {result.stderr}"
    return json.loads(result.stdout)


def test_agent_returns_valid_json_with_required_fields():
    data = _run_agent("What is 2+2?")
    assert "answer" in data, "Missing 'answer' field in output"
    assert "tool_calls" in data, "Missing 'tool_calls' field in output"
    assert isinstance(data["answer"], str), "'answer' must be a string"
    assert len(data["answer"]) > 0, "'answer' must not be empty"
    assert isinstance(data["tool_calls"], list), "'tool_calls' must be a list"


def test_agent_reads_wiki_for_merge_conflict_question():
    data = _run_agent("How do you resolve a merge conflict?")
    assert "source" in data, "Missing 'source' field in output"
    assert "tool_calls" in data
    tool_names = [tc["tool"] for tc in data["tool_calls"]]
    assert "read_file" in tool_names, "Expected read_file to be called"
    assert "wiki/git-workflow.md" in data["source"], "Expected source to reference wiki/git-workflow.md"


def test_agent_lists_wiki_files():
    data = _run_agent("What files are in the wiki?")
    assert "tool_calls" in data
    tool_names = [tc["tool"] for tc in data["tool_calls"]]
    assert "list_files" in tool_names, "Expected list_files to be called"
