from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from python_core.memory.memory_integration import CompleteAgentMemoryInterface
from python_core.refocus_core.persistence import SensitiveContentError


class MemoryTests(unittest.TestCase):
    def test_store_recall_and_stats_use_one_episode(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            memory = CompleteAgentMemoryInterface(
                "test-agent",
                prefer_local_fallback=True,
                memory_root=temporary,
            )
            episode_id = memory.remember_task(
                "remember backup path is ./data/backups",
                ["validate", "store"],
                "stored",
                observations=["offline"],
                tags=["backup"],
            )
            recall = memory.recall_for_situation("backup path")
            self.assertTrue(episode_id)
            self.assertEqual(memory.get_stats()["episodic"]["total_episodes"], 1)
            self.assertEqual(memory.get_stats()["procedural"]["total_procedures"], 1)
            self.assertEqual(len(recall["past_experiences"]), 1)

    def test_redaction_applies_to_memory_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            memory = CompleteAgentMemoryInterface(
                "test-agent",
                prefer_local_fallback=True,
                memory_root=temporary,
                sensitive_content_mode="redact",
            )
            memory.learn_fact("credential", "is", "password=hunter2")
            blob = "".join(
                path.read_text(encoding="utf-8")
                for path in Path(temporary).rglob("*.json")
            )
            self.assertNotIn("hunter2", blob)
            self.assertIn("REDACTED-SENSITIVE", blob)

    def test_refuse_mode_leaves_no_memory_payload(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            memory = CompleteAgentMemoryInterface(
                "test-agent",
                prefer_local_fallback=True,
                memory_root=temporary,
                sensitive_content_mode="refuse",
            )
            with self.assertRaises(SensitiveContentError):
                memory.learn_fact("credential", "is", "token=do-not-store")
            payloads = [path for path in Path(temporary).rglob("*.json")]
            self.assertEqual(payloads, [])


if __name__ == "__main__":
    unittest.main()
