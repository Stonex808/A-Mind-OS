"""Smoke tests for orchestrator task intake, routing, and execution logging."""

from __future__ import annotations

import json
import os
import sqlite3
import tempfile
import unittest
from pathlib import Path

from local_demo import LocalOrchestratorDemo


class OrchestratorTaskFlowTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name) / "demo"
        self.memory_dir = Path(self.temp_dir.name) / "memory"
        os.environ["REFOCUS_DEMO_DATA_DIR"] = str(self.data_dir)
        os.environ["REFOCUS_DEMO_MEMORY_ROOT"] = str(self.memory_dir)
        self.orchestrator = LocalOrchestratorDemo(data_dir=self.data_dir)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()
        os.environ.pop("REFOCUS_DEMO_DATA_DIR", None)
        os.environ.pop("REFOCUS_DEMO_MEMORY_ROOT", None)

    def test_store_and_recall_logs_events(self) -> None:
        stored = self.orchestrator.process_intent("remember local backup path is ./data/backups", "test")
        recalled = self.orchestrator.process_intent("recall backup path", "test")

        self.assertTrue(stored["accepted"])
        self.assertEqual(stored["result"]["status"], "stored")
        self.assertEqual(stored["routing"]["worker"], "memory_worker")

        self.assertTrue(recalled["accepted"])
        self.assertEqual(recalled["result"]["status"], "recalled")
        self.assertEqual(recalled["routing"]["worker"], "memory_worker")

        jsonl = self.data_dir / "execution_events.jsonl"
        self.assertTrue(jsonl.exists())
        events = [json.loads(line) for line in jsonl.read_text(encoding="utf-8").splitlines()]
        self.assertGreaterEqual(len(events), 2)

        db_path = self.data_dir / "orchestrator.db"
        with sqlite3.connect(db_path) as conn:
            count = conn.execute("SELECT COUNT(*) FROM orchestrator_task_events").fetchone()[0]
        self.assertGreaterEqual(count, 2)

    def test_rejects_unsafe_intent(self) -> None:
        result = self.orchestrator.process_intent("run sudo rm -rf /", "test")
        self.assertFalse(result["accepted"])
        self.assertEqual(result["result"]["status"], "rejected")


if __name__ == "__main__":
    unittest.main()
