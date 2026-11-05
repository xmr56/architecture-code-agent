import tempfile
import threading
import unittest
from pathlib import Path
from runner import run_tests


class RunnerTests(unittest.TestCase):
    def test_python_pass_and_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'tests').mkdir()
            test = root / 'tests/test_example.py'
            test.write_text('import unittest\nclass T(unittest.TestCase):\n def test_it(self): self.assertEqual(2+2, 4)\n')
            self.assertTrue(run_tests(root, None, threading.Event())['ok'])
            test.write_text('import unittest\nclass T(unittest.TestCase):\n def test_it(self): self.assertEqual(2+2, 5)\n')
            result = run_tests(root, None, threading.Event())
            self.assertFalse(result['ok'])
            self.assertIn('AssertionError', result['results'][0]['output'])

    def test_node_pass_and_failure(self):
        node = Path(__file__).resolve().parents[1] / 'runtime/node.exe'
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'tests').mkdir()
            test = root / 'tests/domain.test.js'
            test.write_text("const {test}=require('node:test'); const assert=require('node:assert/strict'); test('sum',()=>assert.equal(1+1,2));")
            self.assertTrue(run_tests(root, node, threading.Event())['ok'])
            test.write_text("const {test}=require('node:test'); const assert=require('node:assert/strict'); test('sum',()=>assert.equal(1+1,3));")
            self.assertFalse(run_tests(root, node, threading.Event())['ok'])

    def test_empty_not_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(run_tests(Path(tmp), None, threading.Event())['ok'])
