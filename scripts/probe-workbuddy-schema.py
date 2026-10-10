"""Read only SQLite structure metadata; application row reads and all writes are denied."""
import argparse
import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
READ_PRAGMAS = {
    "table_xinfo", "foreign_key_list", "index_list", "index_xinfo",
    "user_version", "application_id", "schema_version", "journal_mode",
    "page_size", "encoding", "query_only",
}


def metadata_authorizer(action, first, second, database, trigger):
    if action in (sqlite3.SQLITE_SELECT, sqlite3.SQLITE_TRANSACTION):
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_READ and first in ("sqlite_master", "sqlite_schema"):
        return sqlite3.SQLITE_OK
    if action == sqlite3.SQLITE_PRAGMA and first.lower() in READ_PRAGMAS:
        # An argument is permitted only for catalog introspection, never assignments.
        if second is None or first.lower() in {"table_xinfo", "foreign_key_list", "index_list", "index_xinfo"}:
            return sqlite3.SQLITE_OK
    return sqlite3.SQLITE_DENY


def probe(database):
    database = Path(database).resolve(strict=True)
    connection = sqlite3.connect(database.as_uri() + "?mode=ro", uri=True, timeout=2)
    try:
        connection.execute("PRAGMA query_only=ON")
        connection.execute("PRAGMA trusted_schema=OFF")
        connection.set_authorizer(metadata_authorizer)
        connection.execute("BEGIN")
        objects = []
        # SQL LIKE is intentionally avoided; no SQL functions are authorized.
        for kind, name, table, sql in connection.execute("SELECT type,name,tbl_name,sql FROM sqlite_schema ORDER BY type,name").fetchall():
            if name.startswith("sqlite_"):
                continue
            item = {"type": kind, "name": name, "table": table, "sql": sql}
            if kind == "table":
                quoted = '"' + name.replace('"', '""') + '"'
                for pragma, key, fields in (
                    ("table_xinfo", "columns", ["cid", "name", "type", "notnull", "default", "pk", "hidden"]),
                    ("foreign_key_list", "foreign_keys", ["id", "seq", "table", "from", "to", "on_update", "on_delete", "match"]),
                    ("index_list", "indexes", ["seq", "name", "unique", "origin", "partial"]),
                ):
                    item[key] = [dict(zip(fields, row)) for row in connection.execute(f"PRAGMA {pragma}({quoted})")]
            objects.append(item)
        metadata = {name: connection.execute("PRAGMA " + name).fetchone()[0] for name in (
            "user_version", "application_id", "schema_version", "journal_mode", "page_size", "encoding"
        )}
        result = {
            "database": str(database), "connection_mode": "ro",
            "query_only": bool(connection.execute("PRAGMA query_only").fetchone()[0]),
            "application_rows_selected": False, "production_sql_writes_attempted": False,
            "metadata": metadata, "objects": objects,
            "schema_sha256": hashlib.sha256(json.dumps(objects, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
        }
        connection.rollback()
        return result
    finally:
        connection.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", required=True, help="PE FileVersion independently read from the installed official executable")
    args = parser.parse_args()
    if not re.fullmatch(r"\d+(\.\d+){2,3}", args.version):
        parser.error("A numeric observed file version is required")
    data_root = Path.home() / ".workbuddy"
    # Resolve only expected database filenames, not auth, logs, bodies or settings.
    databases = [data_root / "workbuddy.db"] + sorted(data_root.glob("edge-sync-mapping*.db"))
    results = []
    for database in databases:
        if database.name != "workbuddy.db" and not re.fullmatch(r"edge-sync-mapping(?:-v\d+)?\.db", database.name):
            continue
        if database.is_symlink() or database.resolve(strict=True).parent != data_root.resolve(strict=True):
            raise ValueError("Database path escaped the expected data root")
        results.append(probe(database))
    result = {"date": "2026-10-10", "observed_client_file_version": args.version, "scope": "structure metadata only; no credentials or application rows", "databases": results}
    output = ROOT / "docs/evidence/phase08-workbuddy-schema-metadata.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "databases": [{"filename": Path(item["database"]).name, "objects": len(item["objects"]), "schema_sha256": item["schema_sha256"]} for item in results]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
