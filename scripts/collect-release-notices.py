"""Collect local license texts for an intentionally over-inclusive Windows dependency graph.

No network requests, no assumption that package SPDX metadata replaces license texts.
MPL source is retained beside its notices for corresponding-source obligations.
"""
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / 'app'
OUT = APP / 'licenses'
OUT.mkdir(exist_ok=True)
metadata = json.loads((ROOT / 'docs/evidence/phase07-cargo-metadata.json').read_text(encoding='utf-8-sig'))
packages = {p['id']: p for p in metadata['packages']}
nodes = {p['id']: p for p in metadata['resolve']['nodes']}
pending = [p['id'] for p in metadata['packages'] if p['name'] == 'wb-switch-rust']
selected = set()
while pending:
    node = pending.pop()
    if node in selected:
        continue
    selected.add(node)
    pending.extend(d['pkg'] for d in nodes[node]['deps'])

inventory = []
def collect(kind, name, version, expression, directory):
    destination = OUT / kind / re.sub(r'[^a-zA-Z0-9._-]', '_', f'{name}-{version}')
    destination.mkdir(parents=True, exist_ok=True)
    candidates = list(directory.iterdir())
    if kind == 'npm' and name == 'victory-vendor':
        candidates.extend((directory / 'lib-vendor').rglob('LICENSE*'))
    for child in list(candidates):
        if child.is_dir() and child.name.lower() in ('license', 'licenses', 'legal'):
            candidates.extend(child.rglob('*'))
    copied = []
    for file in sorted(candidates):
        if file.is_file() and re.match(r'(?i)^(licen[cs]e|notice|copying|ofl|copyright)', file.name) and file.stat().st_size < 2_000_000:
            relative = file.relative_to(directory)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(file, target)
            copied.append({'path': target.relative_to(APP).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    if kind == 'rust' and expression and 'MPL-2.0' in expression:
        # Unmodified crate source. Cache and generated build outputs are never included.
        source = destination / 'corresponding-source'
        shutil.copytree(directory, source, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git', 'target', '.cargo-ok', '.cargo_vcs_info.json'))
    # Previously downloaded, commit-pinned upstream texts are preserved on reruns.
    for file in sorted(destination.glob('LICENSE-upstream*')):
        if not any(t['path'] == file.relative_to(APP).as_posix() for t in copied):
            copied.append({'path': file.relative_to(APP).as_posix(), 'sha256': hashlib.sha256(file.read_bytes()).hexdigest()})
    inventory.append({'kind': kind, 'name': name, 'version': version, 'license': expression, 'texts': copied})

for node in sorted(selected):
    package = packages[node]
    directory = Path(package['manifest_path']).parent
    expression = package.get('license')
    if directory.is_relative_to(APP) and not expression:
        expression = 'MIT (upstream root LICENSE)'
    collect('rust', package['name'], package['version'], expression, directory)
    if directory.is_relative_to(APP) and not inventory[-1]['texts']:
        target = OUT / 'rust' / f"{package['name']}-{package['version']}" / 'LICENSE'
        shutil.copyfile(APP / 'LICENSE', target)
        inventory[-1]['texts'] = [{'path': target.relative_to(APP).as_posix(), 'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}]

lock = json.loads((APP / 'package-lock.json').read_text(encoding='utf-8'))
for location, package in sorted(lock['packages'].items()):
    if not location or package.get('dev'):
        continue
    directory = APP / location
    if not directory.is_dir():
        continue  # Uninstalled optional platform-specific dependency is not distributed.
    own = json.loads((directory / 'package.json').read_text(encoding='utf-8'))
    collect('npm', own['name'], package['version'], package.get('license') or own.get('license'), directory)

missing = [p for p in inventory if not p['texts']]
(ROOT / 'docs/evidence/phase07-release-license-inventory.json').write_text(json.dumps({'scope': 'Windows desktop metadata closure including build dependencies; installed non-dev npm packages, over-inclusive', 'packages': inventory, 'missing_license_texts': missing}, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
lines = ['# WorkBuddy Manager — Third-party notices', '',
         'Version 0.2.0-alpha.1. This is an independent experimental fork, with no service-provider endorsement.', '',
         'Copyright and full permission notices are retained in the accompanying `licenses/` directory and root `LICENSE`.',
         'Source: workbuddy-switch v0.1.58, commit 9eb3f2a21ff3c3c85fef2f89e693c48792050ba1 (MIT, Copyright (c) 2026 wb-switch).',
         'Helper was consulted as an architectural reference; no Go executable or international simulated-activity implementation is bundled.',
         'The optional Agent Companion runtime and its character artwork are disabled and are not included as installer resources. Its Rust plugin dependency is conservatively listed below.',
         'The original geometric WM product/tray artwork is created for this fork. Third-party product logos are replaced by text marks in the compiled UI.',
         'The Bricolage Grotesque font uses OFL-1.1; its full license is retained. Lucide React uses ISC.',
         'MPL-2.0 crate corresponding source is retained under each crate’s `corresponding-source/` directory, unmodified.',
         'The upstream indexmap 1.9.3 build-script patch is retained in project source (`vendor-patched/indexmap`), with its MIT/Apache notices.',
         'react-remove-scroll-bar 2.3.8 has no license text in its installed package. Its author’s repository license is retained from commit 8ca9ba5ea52de03308fe8ced94f7b159a44d28ff, whose package version is 2.3.7. Exact release-source correspondence is NOT verified; public distribution remains pending this check.',
         'This inventory intentionally includes build dependencies; it is not a symbol-level binary linkage report.', '',
         '| Ecosystem | Package | Version | License | Full text |', '| --- | --- | --- | --- | --- |']
for p in inventory:
    links = ', '.join(f"[{Path(t['path']).name}]({t['path']})" for t in p['texts']) or '**TEXT NOT COLLECTED**'
    lines.append(f"| {p['kind']} | {p['name']} | {p['version']} | {p['license']} | {links} |")
if missing:
    lines += ['', 'Missing texts above require resolution before public distribution. This local candidate is not a final compliance declaration.']
(APP / 'THIRD_PARTY_NOTICES.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(json.dumps({'packages': len(inventory), 'missing': [(p['kind'], p['name'], p['license']) for p in missing]}, ensure_ascii=False))
