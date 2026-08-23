from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from services.orchestrator.local_demo import LocalOrchestratorDemo, LocalVerifier
from services.orchestrator.task_schema import TaskEnvelope, TaskSchemaError


class OrchestratorTests(unittest.TestCase):
    def test_store_and_recall_share_one_logged_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            demo = LocalOrchestratorDemo(data_dir=root / "demo", memory_dir=root / "memory")
            stored = demo.process_intent("remember local backup path is ./data/backups", "test")
            recalled = demo.process_intent("recall backup path", "test")
            self.assertEqual(stored["result"]["status"], "stored")
            self.assertEqual(recalled["result"]["status"], "recalled")
            self.assertEqual(stored["routing"]["worker"], "memory_worker")
            self.assertIn("backup", json.dumps(recalled).lower())
            with sqlite3.connect(root / "demo" / "orchestrator.db") as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM orchestrator_runs").fetchone()[0], 2)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM orchestrator_task_events").fetchone()[0], 2)

    def test_rejected_secret_is_redacted_in_artifact_and_database(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            demo = LocalOrchestratorDemo(data_dir=root / "demo", memory_dir=root / "memory")
            result = demo.process_intent("remember api_key=supersecret", "test")
            self.assertFalse(result["accepted"])
            self.assertEqual(result["result"]["status"], "rejected")
            disk_blob = "".join(
                path.read_text(encoding="utf-8", errors="ignore")
                for path in (root / "demo").rglob("*")
                if path.is_file() and path.suffix != ".db"
            )
            self.assertNotIn("supersecret", disk_blob)
            with sqlite3.connect(root / "demo" / "orchestrator.db") as connection:
                stored_intent = connection.execute(
                    "SELECT raw_intent FROM orchestrator_runs"
                ).fetchone()[0]
            self.assertNotIn("supersecret", stored_intent)

    def test_refuse_mode_writes_no_run_or_event(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch.dict(
            os.environ,
            {"REFOCUS_SENSITIVE_CONTENT_MODE": "refuse"},
        ):
            root = Path(temporary)
            demo = LocalOrchestratorDemo(data_dir=root / "demo", memory_dir=root / "memory")
            result = demo.process_intent("remember token=do-not-store", "test")
            self.assertEqual(result["result"]["status"], "refused")
            self.assertFalse(result["persisted"])
            self.assertEqual(list((root / "demo" / "runs").glob("*.json")), [])
            with sqlite3.connect(root / "demo" / "orchestrator.db") as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM orchestrator_runs").fetchone()[0], 0)
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM orchestrator_task_events").fetchone()[0], 0)

    def test_max_artifact_retention_is_enforced(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch.dict(
            os.environ,
            {"REFOCUS_MAX_RUN_ARTIFACTS": "1"},
        ):
            root = Path(temporary)
            demo = LocalOrchestratorDemo(data_dir=root / "demo", memory_dir=root / "memory")
            demo.process_intent("remember first local fact", "test")
            demo.process_intent("remember second local fact", "test")
            self.assertEqual(len(list((root / "demo" / "runs").glob("*.json"))), 1)
            with sqlite3.connect(root / "demo" / "orchestrator.db") as connection:
                self.assertEqual(connection.execute("SELECT COUNT(*) FROM orchestrator_runs").fetchone()[0], 1)

    def test_verifier_configuration_requires_every_rule(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            rules = Path(temporary) / "rules.json"
            rules.write_text('{"max_intent_length": 100}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "missing required keys"):
                LocalVerifier(rules)

    def test_task_schema_rejects_coerced_payload_types(self) -> None:
        with self.assertRaisesRegex(TaskSchemaError, "content must be a string"):
            TaskEnvelope.from_payload({"kind": "memory", "content": 42, "source": "test"})

    def test_task_schema_requires_utc_and_canonical_id(self) -> None:
        with self.assertRaisesRegex(TaskSchemaError, "task_id must match"):
            TaskEnvelope("memory", "remember this", "test", task_id="wrong").validate()
        local_time = datetime.now(timezone.utc).astimezone(timezone.min)
        with self.assertRaisesRegex(TaskSchemaError, "created_at must be an ISO-8601 UTC string"):
            TaskEnvelope("memory", "remember this", "test", created_at=local_time.isoformat()).validate()


if __name__ == "__main__":
    unittest.main()
