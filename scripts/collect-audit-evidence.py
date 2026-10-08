"""Collect static source and license evidence without reading WorkBuddy data."""
import json
import re
import subprocess
import tomllib
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "evidence"
OUT.mkdir(parents=True, exist_ok=True)

def write(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

pins, symbols, tests = [], [], []
for repo in ("workbuddy-switch", "workbuddy-helper"):
    base = ROOT / "upstream" / repo
    def git(*args):
        return subprocess.check_output(["git", "-C", str(base), *args], text=True, encoding="utf-8").strip()
    pins.append({"repository": repo, "url": git("remote", "get-url", "origin"),
                 "sha": git("rev-parse", "HEAD"), "commit_date": git("show", "-s", "--format=%cI", "HEAD"),
                 "tag": git("describe", "--tags", "--exact-match"),
                 "tracked_changes": git("status", "--porcelain", "--untracked-files=no")})
    folders = ("crates/wb-switch-core", "crates/wb-switch-server", "src-tauri/src", "src") if repo.endswith("switch") else ("cmd", "internal")
    for folder in folders:
        for file in sorted((base / folder).rglob("*")):
            if file.suffix not in (".rs", ".go", ".ts", ".tsx"):
                continue
            lines = file.read_text(encoding="utf-8").splitlines()
            count = 0
            for n, line in enumerate(lines, 1):
                if re.search(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?(?:fn|struct|enum)\s+\w+|^func\s|^type\s", line):
                    symbols.append({"file": file.relative_to(ROOT).as_posix(), "line": n, "declaration": line.strip()})
                if re.search(r"#\[(?:tokio::)?test\]|^func Test\w+", line):
                    count += 1
            if count:
                tests.append({"file": file.relative_to(ROOT).as_posix(), "test_markers": count})
write("upstream-pins.json", pins)
write("source-symbols.json", symbols)
write("test-inventory.json", tests)

npm = []
for folder in ("upstream/workbuddy-switch", "upstream/workbuddy-switch/vendor/agent-companion"):
    base = ROOT / folder
    lock = json.loads((base / "package-lock.json").read_text(encoding="utf-8"))
    for location, item in lock.get("packages", {}).items():
        if not location:
            continue
        installed = base / location / "package.json"
        info = json.loads(installed.read_text(encoding="utf-8")) if installed.is_file() else {}
        npm.append({"lockfile": folder + "/package-lock.json", "path": location, "version": item.get("version"),
                    "license": item.get("license") or info.get("license"), "installed": installed.is_file(),
                    "dev": item.get("dev", False), "optional": item.get("optional", False)})
write("npm-license-inventory.json", npm)

rust = []
registry = Path.home() / ".cargo" / "registry" / "src"
for lockpath in (ROOT / "upstream/workbuddy-switch/Cargo.lock", ROOT / "upstream/workbuddy-switch/vendor/agent-companion/Cargo.lock"):
    for item in tomllib.loads(lockpath.read_text(encoding="utf-8"))["package"]:
        name, version = item["name"], item["version"]
        found = list(registry.glob(f"*/{name}-{version}/Cargo.toml"))
        data = tomllib.loads(found[0].read_text(encoding="utf-8"))["package"] if found else {}
        rust.append({"lockfile": lockpath.relative_to(ROOT).as_posix(), "name": name, "version": version,
                     "source": item.get("source", "local"), "license": data.get("license"),
                     "license_file": data.get("license-file"), "manifest_available": bool(found)})
write("rust-license-inventory.json", rust)
print(json.dumps({"pins": pins, "symbols": len(symbols), "test_files": len(tests),
                  "npm_entries": len(npm), "npm_licenses": dict(Counter(str(x["license"]) for x in npm)),
                  "rust_entries": len(rust), "rust_missing_manifests": sum(not x["manifest_available"] for x in rust)}, ensure_ascii=False, indent=2))
