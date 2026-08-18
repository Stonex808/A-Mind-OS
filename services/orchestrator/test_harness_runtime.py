import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from harness_runtime import (
    AdmissionDecision,
    AdmissionError,
    BudgetError,
    ComputeEconomist,
    LifecycleSupervisor,
    ResourceBudget,
    ToolBroker,
)


class HarnessRuntimeTests(unittest.TestCase):
    def test_tool_requires_scoped_admission(self):
        broker = ToolBroker()
        broker.register("math.add", lambda a, b: a + b)
        economist = ComputeEconomist(ResourceBudget(100, 1000, 1))
        admission = AdmissionDecision(
            admission_id="adm-1",
            actor_id="worker-1",
            intent_id="intent-1",
            action="tool.invoke",
            target="math.add",
            argument_digest="sha256:abc",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=1),
            allowed=True,
        )
        self.assertEqual(
            5,
            broker.invoke(
                name="math.add",
                arguments={"a": 2, "b": 3},
                argument_digest="sha256:abc",
                admission=admission,
                economist=economist,
            ),
        )
        self.assertEqual(1, economist.usage.tool_calls)

    def test_scope_mismatch_fails_closed(self):
        broker = ToolBroker()
        broker.register("math.add", lambda a, b: a + b)
        economist = ComputeEconomist(ResourceBudget(100, 1000, 1))
        admission = AdmissionDecision(
            admission_id="adm-2",
            actor_id="worker-1",
            intent_id="intent-1",
            action="tool.invoke",
            target="math.add",
            argument_digest="sha256:expected",
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=1),
            allowed=True,
        )
        with self.assertRaises(AdmissionError):
            broker.invoke(
                name="math.add",
                arguments={"a": 2, "b": 3},
                argument_digest="sha256:wrong",
                admission=admission,
                economist=economist,
            )

    def test_economist_rejects_oversubscription(self):
        economist = ComputeEconomist(ResourceBudget(10, 100, 1, 1))
        economist.reserve(tokens=8)
        with self.assertRaises(BudgetError):
            economist.reserve(tokens=3)

    def test_lifecycle_marks_stale(self):
        supervisor = LifecycleSupervisor(heartbeat_timeout_seconds=1)
        lease = supervisor.register("worker-1", "research")
        lease.last_heartbeat = datetime.now(timezone.utc) - timedelta(seconds=2)
        supervisor.refresh_health()
        self.assertEqual("STALE", lease.health.value)


if __name__ == "__main__":
    unittest.main()
