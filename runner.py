"""Fixed test commands; execution requires the user's per-run opt-in."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


def install_dependencies(project, node, cancelled):
    if node is None or not node.is_file():
        return {'ok': False, 'error': '缺少Node运行时'}
    npm = node.parent / 'npm/bin/npm-cli.js'
    if not npm.is_file() or not (project / 'package.json').is_file():
        return {'ok': False, 'error': '自动安装目前仅支持Node package.json项目'}
    env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ('KEY', 'TOKEN', 'SECRET', 'PASSWORD'))}
    with tempfile.TemporaryDirectory(prefix='codeagent-install-') as tmp:
        out = Path(tmp) / 'install.txt'
        with out.open('wb') as stream:
            process = subprocess.Popen([str(node), str(npm), 'install', '--ignore-scripts', '--no-audit', '--no-fund', '--cache', str(project.parent / 'npm-cache')], cwd=project, env=env,
                stdout=stream, stderr=stream, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
            import time
            start = time.monotonic()
            interrupted = False
            while process.poll() is None:
                if cancelled.is_set() or time.monotonic()-start > 180:
                    interrupted = True
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                    process.wait(timeout=10)
                    break
                time.sleep(.1)
        return {'ok': process.returncode == 0 and not interrupted, 'exit_code': process.returncode,
                'output': out.read_bytes()[:16000].decode('utf-8', errors='replace'), 'interrupted': interrupted}


def python_child(project, result_path):
    os.chdir(project)
    sys.path.insert(0, str(Path(project).resolve()))
    with open(result_path, 'w', encoding='utf-8') as stream:
        try:
            suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
            if suite.countTestCases() == 0:
                stream.write('ERROR: No Python tests discovered')
                return 2
            result = unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
            return 0 if result.wasSuccessful() else 1
        except BaseException as exc:
            stream.write(repr(exc))
            return 1


def run_tests(project: Path, node: Path | None, cancelled, timeout=60):
    project = project.resolve()
    files = list(project.rglob('*'))
    js_tests = sorted(p for p in files if p.is_file() and 'node_modules' not in p.parts
                      and (p.name.endswith(('.test.js', '.test.mjs', '.spec.js'))
                           or (any(part in ('tests', 'test') for part in p.relative_to(project).parts) and p.suffix in ('.js', '.mjs'))))
    py_tests = [p for p in files if p.name.startswith('test_') and p.suffix == '.py' and 'tests' in p.relative_to(project).parts]
    if not js_tests and not py_tests:
        return {'ok': False, 'error': '没有可执行测试：需要tests/test_*.py或Node tests/*.test.js', 'runtime_tests': 'NO_TESTS'}
    if js_tests and (node is None or not node.is_file()):
        return {'ok': False, 'error': '缺少Node运行时', 'runtime_tests': 'MISSING_RUNTIME'}
    outcomes = []
    # API credentials are never placed in child environment.
    env = {k: v for k, v in os.environ.items() if not any(s in k.upper() for s in ('KEY', 'TOKEN', 'SECRET', 'PASSWORD'))}
    env.update({'PYTHONIOENCODING': 'utf-8', 'PYTHONDONTWRITEBYTECODE': '1'})
    jobs = []
    if js_tests:
        jobs.append(('node', [str(node), '--test'] + [str(p) for p in js_tests]))
    if py_tests:
        args = [sys.executable]
        if not getattr(sys, 'frozen', False):
            args.append(str(Path(__file__).with_name('app.py')))
        jobs.append(('python', args))
    for language, command in jobs:
        with tempfile.TemporaryDirectory(prefix='codeagent-tests-') as temp:
            output = Path(temp) / 'output.txt'
            child_result = Path(temp) / 'python-result.txt'
            if language == 'python':
                command += ['--run-generated-tests', str(project), str(child_result)]
            with output.open('wb') as stream:
                process = subprocess.Popen(command, cwd=project, stdout=stream, stderr=stream,
                    env=env, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
                import time
                started = time.monotonic()
                interrupted = False
                while process.poll() is None:
                    if cancelled.is_set() or time.monotonic() - started > timeout:
                        interrupted = True
                        if os.name == 'nt':
                            subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                creationflags=subprocess.CREATE_NO_WINDOW)
                        else:
                            process.kill()
                        process.wait(timeout=10)
                        break
                    time.sleep(.1)
            text = output.read_bytes()[:24000].decode('utf-8', errors='replace')
            if child_result.exists():
                text += '\n' + child_result.read_text(encoding='utf-8', errors='replace')[:24000]
            code = process.returncode
            # Node can exit zero after discovering no tests; do not count that as success.
            zero_tests = language == 'node' and ('# tests 0' in text or '"tests":0' in text)
            outcomes.append({'language': language, 'exit_code': code, 'output': text,
                             'ok': code == 0 and not interrupted and not zero_tests,
                             'interrupted': interrupted})
    ok = all(row['ok'] for row in outcomes)
    return {'ok': ok, 'runtime_tests': 'PASSED' if ok else 'FAILED', 'results': outcomes,
            'scope': '实际运行生成的测试；测试通过不能证明测试覆盖所有需求。'}
