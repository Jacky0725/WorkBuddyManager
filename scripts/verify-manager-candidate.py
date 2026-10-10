"""Offline byte-integrity check; this does not certify production compatibility or licensing."""
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CANDIDATE = ROOT / "release/0.2.0-alpha.1/local-candidate"


def sha256(path):
    with path.open("rb") as stream:
        digest = hashlib.sha256()
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def checked_file(relative):
    path = (CANDIDATE / relative).resolve()
    if not path.is_relative_to(CANDIDATE.resolve()) or not path.is_file():
        raise ValueError(f"Missing or escaped candidate file: {relative}")
    return path


manifest = json.loads((CANDIDATE / "manifest.json").read_text(encoding="utf-8-sig"))
assert manifest == json.loads((ROOT / "docs/evidence/windows-manager-artifacts.json").read_text(encoding="utf-8-sig")), "Tracked artifact record differs from candidate"
app_commit = manifest["app_commit"]
# Historical candidates remain verifiable after later development commits.
resolved_commit = subprocess.check_output(["git", "-C", str(ROOT / "app"), "rev-parse", "--verify", app_commit + "^{commit}"], text=True).strip()
assert resolved_commit == app_commit, "Candidate commit is not available in the retained app history"
names = set()
for entry in manifest["files"]:
    assert entry["name"] not in names, f"Duplicate manifest entry: {entry['name']}"
    names.add(entry["name"])
    path = checked_file(entry["name"])
    assert path.stat().st_size == entry["bytes"], f"Size mismatch: {entry['name']}"
    assert sha256(path) == entry["sha256"], f"Hash mismatch: {entry['name']}"
actual_names = {
    path.relative_to(CANDIDATE).as_posix()
    for path in CANDIDATE.rglob("*") if path.is_file()
    and path.name not in ("manifest.json", "SHA256SUMS.txt")
}
assert names == actual_names, "Manifest does not cover all payload files"
sum_rows = {}
for line in (CANDIDATE / "SHA256SUMS.txt").read_text(encoding="utf-8-sig").splitlines():
    digest, relative = line.split("  ", 1)
    assert relative not in sum_rows, f"Duplicate checksum: {relative}"
    sum_rows[relative] = digest
assert sum_rows == {item["name"]: item["sha256"] for item in manifest["files"]}, "Checksum list differs from manifest"
required = {
    "LICENSE", "THIRD_PARTY_NOTICES.md", "README.md", "INSTALLATION.md",
    "RELEASE_NOTES.md", "KNOWN_LIMITATIONS.md", "TEST_REPORT.md", "USER_GUIDE.md",
    "SECURITY_REVIEW.md", "ACCEPTANCE_PLAN.md", "app-development.bundle",
    "WorkBuddy Manager_0.2.0-alpha.1_x64-setup.exe", "workbuddy-manager.exe",
    "WorkBuddyManager-0.2.0-alpha.1-source.zip",
}
assert required <= names, "Required delivery files are missing"
inventory = json.loads(checked_file("evidence/phase07-release-license-inventory.json").read_text(encoding="utf-8-sig"))
license_text_count = 0
mpl_sources = []
for package in inventory["packages"]:
    assert package["texts"], f"No license text: {package['name']}"
    for entry in package["texts"]:
        assert sha256(checked_file(entry["path"])) == entry["sha256"].upper(), f"License text differs: {entry['path']}"
        license_text_count += 1
    if "MPL-2.0" in (package["license"] or ""):
        source = CANDIDATE / "licenses/rust" / f"{package['name']}-{package['version']}" / "corresponding-source"
        assert (source / "Cargo.toml").is_file(), f"MPL corresponding source missing: {package['name']}"
        mpl_sources.append(f"{package['name']} {package['version']}")
with zipfile.ZipFile(checked_file("WorkBuddyManager-0.2.0-alpha.1-source.zip")) as archive:
    assert archive.testzip() is None, "Source archive CRC failure"
    archive_names = set(archive.namelist())
    for path in ("Cargo.lock", "package-lock.json", "LICENSE", "THIRD_PARTY_NOTICES.md", "src-tauri/tauri.conf.json"):
        assert path in archive_names, f"Source archive incomplete: {path}"
    config = json.loads(archive.read("src-tauri/tauri.conf.json"))
    assert config["version"] == manifest["version"], "Source version mismatch"
    for relative in names:
        if relative.startswith("licenses/"):
            assert relative in archive_names, f"License/source not retained in app source: {relative}"
            assert hashlib.sha256(archive.read(relative)).hexdigest().upper() == sha256(checked_file(relative)), f"Installed license/source differs from committed archive: {relative}"
source_process = subprocess.Popen(["git", "-C", str(ROOT / "app"), "archive", "--format=zip", app_commit], stdout=subprocess.PIPE)
source_digest = hashlib.sha256()
for block in iter(lambda: source_process.stdout.read(1024 * 1024), b""):
    source_digest.update(block)
source_process.stdout.close()
assert source_process.wait() == 0, "Git source archive comparison failed"
assert source_digest.hexdigest().upper() == sha256(checked_file("WorkBuddyManager-0.2.0-alpha.1-source.zip")), "Source archive differs from recorded Git commit"
bundle = checked_file("app-development.bundle")
subprocess.run(["git", "-C", str(ROOT / "app"), "bundle", "verify", str(bundle)], check=True, capture_output=True)
heads = subprocess.check_output(["git", "bundle", "list-heads", str(bundle)], text=True)
assert f"{app_commit} refs/heads/develop/workbuddy-manager" in heads, "Bundle head differs from candidate"
assert not manifest["real_account_tests_executed"] and not manifest["production_checkin_enabled"] and not manifest["production_session_writes_enabled"]
assert manifest["license_release_source_correspondence_verified"] is False
result = {
    "date": "2026-10-10", "app_commit": app_commit,
    "payload_files_verified": len(names), "license_packages": len(inventory["packages"]),
    "license_text_hashes_verified": license_text_count, "mpl_sources_present": mpl_sources,
    "source_zip_crc_valid": True, "source_archive_matches_git_commit": True,
    "installed_dependency_license_and_corresponding_source_matches_git_archive": True, "development_bundle_valid": True,
    "all_payload_sha256_valid": True, "checksum_list_matches": True,
    "real_account_compatibility_certified": False, "public_distribution_license_review_complete": False,
}
(ROOT / "docs/evidence/manager-candidate-verification.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print(json.dumps(result, ensure_ascii=False))
