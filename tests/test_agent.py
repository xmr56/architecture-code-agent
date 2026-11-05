import json
import tempfile
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from core import Agent, DeepSeek, Workspace, preprocess
from selfcheck import FixtureClient, run_check


class AgentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name)

    def test_repair_feedback_loop(self):
        self.assertIn("PASS", run_check())

    def test_empty_and_oversized_input_rejected(self):
        for doc, view in [("", "x"), ("x", ""), ("x" * 150001, "x")]:
            with self.assertRaises(ValueError):
                preprocess(doc, view)

    def test_preprocessing_preserves_original_and_fenced_headings(self):
        doc = "# Real\n```md\n# Not a section\n```\n## Next\ncontent"
        data = preprocess(doc, "```plantuml\n@startuml\n@enduml\n```")
        self.assertEqual(data["document"], doc)
        self.assertEqual([s["heading"] for s in data["sections"]], ["Preamble", "Real", "Next"])
        self.assertEqual(len(data["plantuml_blocks"]), 1)

    def test_path_escape_windows_special_paths_and_size(self):
        ws = Workspace(self.path)
        for path in ["../x", "/x", "D:/x", "a\\b", "NUL", "CON.txt", "a/COM1.log", "a.", "a ", "a:stream", "a//b"]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                ws.write(path, "text")
        with self.assertRaises(ValueError):
            ws.write("large.txt", "x" * 200001)
        ws.write("src/hello.py", "print('hello')")
        self.assertEqual(ws.read("src/hello.py"), "print('hello')")

    def test_validation_does_not_execute_source(self):
        ws = Workspace(self.path)
        ws.write("main.py", "raise RuntimeError('must not execute')")
        ws.write("README.md", "run instructions")
        ws.write("requirements.txt", "")
        ws.write("tests/test_app.py", "raise RuntimeError('not executed')")
        self.assertTrue(ws.validate()["ok"])
        self.assertEqual(ws.validate()["runtime_tests"], "NOT_RUN")
        ws.write("package.json", "{broken")
        self.assertFalse(ws.validate()["ok"])

    def test_dependencies_are_never_listed_or_editable(self):
        ws = Workspace(self.path)
        (self.path/'node_modules/example').mkdir(parents=True)
        (self.path/'node_modules/example/config.json').write_text('{invalid third party json}')
        self.assertEqual(ws.files(), [])
        with self.assertRaises(ValueError):
            ws.write('node_modules/example/config.json', '{}')
        with self.assertRaises(ValueError):
            ws.read('node_modules/example/config.json')

    def test_cancellation_before_api_and_unique_runs(self):
        stop = threading.Event()
        stop.set()
        client = FixtureClient()
        a = Agent(client, self.path, cancel=stop)
        b = Agent(client, self.path)
        self.assertNotEqual(a.run_dir, b.run_dir)
        report = a.run(preprocess("a", "b"))
        self.assertEqual(report["status"], "cancelled")
        self.assertEqual(client.step, 0)

    def test_budget_exhaustion_not_success(self):
        a = Agent(FixtureClient(), self.path, max_rounds=1)
        self.assertEqual(a.run(preprocess("a", "b"))["status"], "limit_reached")

    def test_cancel_after_response_does_not_write(self):
        stop = threading.Event()
        class Client(FixtureClient):
            def complete(self, messages):
                response = super().complete(messages)
                stop.set()
                return response
        a = Agent(Client(), self.path, cancel=stop)
        report = a.run(preprocess("a", "b"))
        self.assertEqual(report["status"], "cancelled")
        self.assertEqual(a.ws.files(), [])

    def test_official_request_shape_without_network(self):
        class Response:
            def __enter__(self): return self
            def __exit__(self, *args): pass
            def read(self):
                return json.dumps({"choices": [{"message": {"role": "assistant", "content": "ok"}, "finish_reason": "stop"}]}).encode()
        with patch("urllib.request.urlopen", return_value=Response()) as call:
            DeepSeek("fake-test-key").complete([{"role": "user", "content": "hello"}])
        req = call.call_args.args[0]
        body = json.loads(req.data)
        self.assertEqual(req.full_url, "https://api.deepseek.com/chat/completions")
        self.assertEqual(body["model"], "deepseek-v4-pro")
        self.assertEqual(body["thinking"]["type"], "disabled")
        self.assertEqual(len(body["tools"]), 7)


if __name__ == "__main__":
    unittest.main()
