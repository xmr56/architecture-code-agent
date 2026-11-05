"""Download an official, pinned Windows x64 Node runtime, verifying SHA256."""
import hashlib
import shutil
import tempfile
import urllib.request
import zipfile
from pathlib import Path

VERSION = '24.22.1'
SHA256 = 'd2046d28c2c3dcd211ac5145c0bf30e2047ef9dfb306693c8c6e2eccd8b95fa5'
ROOT = Path(__file__).resolve().parent


def main():
    name = f'node-v{VERSION}-win-x64'
    url = f'https://nodejs.org/dist/v{VERSION}/{name}.zip'
    target = ROOT / 'runtime'
    if (target/'node.exe').exists() and (target/'npm/bin/npm-cli.js').exists():
        print('Runtime already present. To refresh it, move runtime/ aside and rerun.')
        return
    with tempfile.TemporaryDirectory(prefix='codeagent-runtime-') as temp:
        archive = Path(temp)/'node.zip'
        print('Downloading official runtime:', url)
        with urllib.request.urlopen(url, timeout=180) as response, archive.open('wb') as stream:
            shutil.copyfileobj(response, stream)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != SHA256:
            raise RuntimeError('SHA256 mismatch: do not use this download')
        unpack = Path(temp)/'unpacked'
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                if not (unpack/item.filename).resolve().is_relative_to(unpack.resolve()):
                    raise RuntimeError('Invalid archive path')
            z.extractall(unpack)
        source = unpack/name
        target.mkdir(exist_ok=True)
        shutil.copy2(source/'node.exe', target/'node.exe')
        shutil.copytree(source/'node_modules/npm', target/'npm', dirs_exist_ok=True)
        shutil.copy2(source/'LICENSE', target/'NODE-LICENSE.txt')
    print('Ready: runtime/node.exe and runtime/npm/')


if __name__ == '__main__':
    main()
