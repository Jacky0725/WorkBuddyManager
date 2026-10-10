"""Check the metadata-only guard using fictional data; never opens a production path."""
import importlib.util
from contextlib import closing
import sqlite3
import tempfile
import unittest
from pathlib import Path

module_spec = importlib.util.spec_from_file_location("probe", Path(__file__).with_name("probe-workbuddy-schema.py"))
probe = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(probe)


class MetadataGuardTests(unittest.TestCase):
    def setUp(self):
        self.fixture_parent = probe.ROOT / "test-fixtures/phase08-metadata-guard"
        self.fixture_parent.mkdir(parents=True, exist_ok=True)
        self.directory = tempfile.TemporaryDirectory(prefix="wbm-metadata-guard-", dir=self.fixture_parent)
        self.path = Path(self.directory.name) / "workbuddy.db"
        with closing(sqlite3.connect(self.path)) as connection:
            connection.executescript("CREATE TABLE sessions(id TEXT PRIMARY KEY, secret TEXT); INSERT INTO sessions VALUES('fiction','DO_NOT_RETURN_FICTION_SECRET');")

    def tearDown(self):
        if Path(self.directory.name).resolve().parent != self.fixture_parent.resolve():
            raise ValueError("Temporary cleanup escaped the isolated fixture directory")
        self.directory.cleanup()

    def test_probe_returns_structure_without_rows_and_preserves_database_bytes(self):
        before = self.path.read_bytes()
        result = probe.probe(self.path)
        self.assertTrue(result["query_only"])
        self.assertEqual(result["objects"][0]["name"], "sessions")
        self.assertNotIn("DO_NOT_RETURN_FICTION_SECRET", str(result))
        self.assertEqual(self.path.read_bytes(), before)

    def test_guard_blocks_application_reads_writes_attachments_and_pragma_assignments(self):
        connection = sqlite3.connect(self.path)
        try:
            connection.set_authorizer(probe.metadata_authorizer)
            for statement in (
                "SELECT secret FROM sessions", "SELECT count(*) FROM sessions",
                "UPDATE sessions SET secret='changed'", "DROP TABLE sessions",
                "ATTACH ':memory:' AS outside", "PRAGMA user_version=99", "PRAGMA journal_mode=DELETE",
            ):
                with self.subTest(statement=statement), self.assertRaises(sqlite3.DatabaseError):
                    connection.execute(statement)
        finally:
            connection.close()

    def test_uncheckpointed_wal_schema_is_visible(self):
        writer = sqlite3.connect(self.path)
        try:
            writer.executescript("PRAGMA journal_mode=WAL; PRAGMA wal_autocheckpoint=0; CREATE TABLE wal_only(id TEXT); INSERT INTO wal_only VALUES('fiction');")
            self.assertGreater(Path(str(self.path) + "-wal").stat().st_size, 0)
            result = probe.probe(self.path)
            self.assertEqual(result["metadata"]["journal_mode"], "wal")
            self.assertIn("wal_only", [item["name"] for item in result["objects"]])
        finally:
            writer.close()


if __name__ == "__main__":
    unittest.main(verbosity=2)
