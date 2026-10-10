"""Fetch license texts from package-pinned upstream commits, never latest HEAD."""
import concurrent.futures
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / 'app'
metadata = json.loads((ROOT / 'docs/evidence/phase07-cargo-metadata.json').read_text(encoding='utf-8-sig'))
inventory = json.loads((ROOT / 'docs/evidence/phase07-release-license-inventory.json').read_text(encoding='utf-8'))
packages = {p['name']: p for p in metadata['packages']}
def read_url(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={'User-Agent': 'WorkBuddyManager-license-audit'}), timeout=25).read()
def fetch(package):
    name, version, kind = package['name'], package['version'], package['kind']
    if kind == 'rust':
        own = packages[name]
        vcs = json.loads((Path(own['manifest_path']).parent / '.cargo_vcs_info.json').read_text())
        sha = vcs['git']['sha1']
        repo = own['repository'].rstrip('/').removesuffix('.git')
        subdir = vcs.get('path_in_vcs', '').strip('/')
    else:
        own = json.loads(read_url(f'https://registry.npmjs.org/{name}/{version}'))
        sha = own['gitHead']
        repo = own['repository']['url'].replace('git+', '').replace('git://', 'https://').removesuffix('.git').rstrip('/')
        subdir = own['repository'].get('directory', '')
    if not repo.startswith('https://github.com/') or len(sha) != 40:
        raise ValueError(f'Unverified source for {name}')
    base = repo.replace('https://github.com/', 'https://raw.githubusercontent.com/') + '/' + sha + '/'
    paths = [f'{subdir}/{filename}'.lstrip('/') for filename in ('LICENSE', 'LICENSE-MIT', 'LICENSE-APACHE', 'LICENSE.md', 'LICENSE.txt', 'COPYING')]
    paths += ['LICENSE', 'LICENSE-MIT', 'LICENSE-APACHE', 'LICENSE.md', 'LICENSE.txt', 'COPYING']
    records = []
    for relative in dict.fromkeys(paths):
        try:
            content = read_url(base + relative)
        except Exception:
            continue
        if len(content) < 100 or len(content) > 200_000:
            continue
        target = APP / 'licenses' / kind / f'{name}-{version}' / ('LICENSE-upstream-' + relative.replace('/', '_'))
        target.write_bytes(content)
        records.append({'package': name, 'version': version, 'url': base + relative, 'sha256': hashlib.sha256(content).hexdigest(), 'path': target.relative_to(APP).as_posix()})
    return {'name': name, 'texts': records}
results = []
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
    tasks = {pool.submit(fetch, p): p for p in inventory['missing_license_texts']}
    for future in concurrent.futures.as_completed(tasks):
        try:
            result = future.result()
        except Exception as error:
            result = {'name': tasks[future]['name'], 'error': str(error)}
        results.append(result)
        print(result['name'], len(result.get('texts', [])), result.get('error', ''), flush=True)
(ROOT / 'docs/evidence/phase07-license-text-provenance.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
