"""Read selected installed program text as data; never execute code or open user data."""
import hashlib
import json
import re
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = Path(r"D:\Program Files\WorkBuddy\resources\app.asar")
MEMBERS = ("main/conversations.js", "main/handlers.js", "main/server.js")


def inspect():
    size = ARCHIVE.stat().st_size
    with ARCHIVE.open("rb") as stream:
        prefix, header_size, payload_size, json_size = struct.unpack("<4I", stream.read(16))
        if prefix != 4 or not (0 < json_size <= 8 * 1024 * 1024) or header_size != payload_size + 4:
            raise ValueError("Unexpected ASAR header")
        base = 8 + header_size
        if 16 + json_size > base or base > size:
            raise ValueError("ASAR header bounds are invalid")
        catalog = json.loads(stream.read(json_size))
        members = {}
        for name in MEMBERS:
            entry = catalog
            for part in name.split("/"):
                entry = entry["files"][part]
            if entry.get("unpacked") or "link" in entry:
                raise ValueError("Selected member is not a packed regular file")
            offset, length = int(entry["offset"]), entry["size"]
            if offset < 0 or not (0 < length <= 8 * 1024 * 1024) or base + offset + length > size:
                raise ValueError("Selected member bounds are invalid")
            stream.seek(base + offset)
            data = stream.read(length)
            if len(data) != length:
                raise ValueError("Truncated selected member")
            text = data.decode("utf-8")
            facts = []
            patterns = {
                "local_active_predicate": r"transport = 'local'\s+AND deleted_at IS NULL",
                "cloud_active_predicate": r"transport = 'cloud'\s+AND deleted_at = -1",
                "cloud_deleted_normalization": r"CASE WHEN deleted_at = -1 THEN NULL ELSE deleted_at END AS deletedAt",
                "cloud_upsert_sentinel": r"qC=-1,JC=",
                "buddy_binding_reference_check": r"t\.snapshotId!==e\.buddySnapshotId",
                "buddy_snapshot_lookup": r"FROM buddy_snapshots",
            }
            for key, pattern in patterns.items():
                matches = list(re.finditer(pattern, text))
                if matches:
                    first = matches[0]
                    start, end = max(0, first.start() - 90), min(len(text), first.end() + 150)
                    facts.append({"fact": key, "matches": len(matches), "character_offset": first.start(),
                                  "excerpt_start": start, "excerpt": text[start:end]})
            members[name] = {"bytes": length, "sha256": hashlib.sha256(data).hexdigest(), "facts": facts}
    with ARCHIVE.open("rb") as stream:
        archive_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    return {"date": "2026-10-10", "archive": str(ARCHIVE), "archive_bytes": size,
            "archive_sha256": archive_hash, "source_kind": "Installed 5.7.7 program text, static observation only",
            "program_code_executed": False, "user_data_opened": False, "production_sql_writes_attempted": False,
            "members": members}


if __name__ == "__main__":
    result = inspect()
    output = ROOT / "docs/evidence/phase09-installed-code-facts.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "facts": {name: [fact["fact"] for fact in member["facts"]]
                                                      for name, member in result["members"].items()}}, ensure_ascii=False))
