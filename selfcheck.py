"""Offline integration fixture. Explicitly NOT a model-generated project."""
import json
import tempfile
from pathlib import Path
from core import Agent, preprocess


class FixtureClient:
    def __init__(self):
        self.step = 0

    def complete(self, messages):
        self.step += 1
        if self.step == 1:
            actions = [("write_file", {"path": "main.py", "content": "def broken(\n"}),
                       ("write_file", {"path": "README.md", "content": "Offline fixture, not an AI output."}),
                       ("write_file", {"path": "requirements.txt", "content": "# standard library\n"}),
                       ("write_file", {"path": "tests/test_main.py", "content": "import unittest\nclass T(unittest.TestCase):\n def test_add(self):\n  from main import add\n  self.assertEqual(add(2, 3), 5)\n"}),
                       ("validate_project", {})]
        elif self.step == 2:
            assert any("never closed" in (m.get("content") or "") for m in messages), "Expected syntax feedback"
            actions = [("write_file", {"path": "main.py", "content": "def add(a, b):\n    return a + b\n"}),
                       ("finish", {"summary": "Offline fixture repaired"})]
        else:
            raise AssertionError("Unexpected extra round")
        return {"message": {"role": "assistant", "content": None, "tool_calls": [
            {"id": f"call_{self.step}_{i}", "type": "function", "function": {"name": n, "arguments": json.dumps(a)}}
            for i, (n, a) in enumerate(actions)]}, "usage": {"total_tokens": 0}}


def run_check():
    with tempfile.TemporaryDirectory(prefix="codeagent-selfcheck-") as directory:
        agent = Agent(FixtureClient(), Path(directory), max_rounds=3)
        report = agent.run(preprocess("# Example\nOffline fixture", "```plantuml\n@startuml\n@enduml\n```"))
        assert report["status"] == "artifacts_ready", report
        assert report["validation"]["ok"], report
        assert report["runtime_tests"] == "NOT_RUN"
        for bad in ("../escape.py", "C:/outside.py", "NUL.txt", "folder/../../x", "a:stream", "/absolute.py"):
            try:
                agent.ws.write(bad, "x")
            except ValueError:
                pass
            else:
                raise AssertionError("Path was not rejected: " + bad)
    return "PASS：离线工具调用→发现语法错误→反馈→修复→保存报告；目录越界检查通过。"
