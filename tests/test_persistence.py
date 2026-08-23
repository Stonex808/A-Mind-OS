from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from python_core.refocus_core.logging import setup_logging
from python_core.refocus_core.persistence import (
    REDACTION_TEXT,
    PersistenceConfigurationError,
    SensitiveContentError,
    load_demo_persistence_settings,
    sanitize_for_local_persistence,
)


class PersistenceTests(unittest.TestCase):
    def test_nested_values_are_redacted(self) -> None:
        clean = sanitize_for_local_persistence(
            {"message": "password=hunter2", "items": ["token: abcdef", "safe"]},
            "redact",
        )
        self.assertNotIn("hunter2", json.dumps(clean))
        self.assertNotIn("abcdef", json.dumps(clean))
        self.assertIn(REDACTION_TEXT, json.dumps(clean))

    def test_sensitive_mapping_keys_are_also_redacted(self) -> None:
        clean = sanitize_for_local_persistence({"token=abcdef": "safe"}, "redact")
        self.assertNotIn("abcdef", json.dumps(clean))

    def test_refuse_mode_raises_before_write(self) -> None:
        with self.assertRaises(SensitiveContentError):
            sanitize_for_local_persistence("api_key=do-not-store", "refuse")

    def test_invalid_config_fails_clearly(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            config = Path(temporary) / "config.toml"
            config.write_text("[local_persistence.demo]\nretention_days = -1\n", encoding="utf-8")
            with self.assertRaisesRegex(PersistenceConfigurationError, "non-negative"):
                load_demo_persistence_settings(config_path=config)

    def test_explicit_data_directory_keeps_all_demo_artifacts_together(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "portable-demo"
            settings = load_demo_persistence_settings(data_dir=root, environ={})
            self.assertEqual(settings.runs_dir, root / "runs")
            self.assertEqual(settings.db_path, root / "orchestrator.db")
            self.assertEqual(settings.memory_dir, root / "memory")

    def test_logging_setup_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            first = setup_logging("a-mind-test-logger", Path(temporary))
            second = setup_logging("a-mind-test-logger", Path(temporary))
            self.assertIs(first, second)
            self.assertEqual(len(first.handlers), 1)
            first.info("verified")
            lines = (Path(temporary) / "a-mind-test-logger.jsonl").read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(lines), 1)


if __name__ == "__main__":
    unittest.main()
