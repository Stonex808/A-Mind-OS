import unittest
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from local_demo import LocalOrchestratorDemo
from planner_worker import LocalPlanner, PlannerWorkerOrchestrator, WorkerRegistry


class PlannerWorkerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.demo = LocalOrchestratorDemo()

    def _build_stack(self):
        planner = LocalPlanner()
        registry = WorkerRegistry()
        registry.register(self.demo.memory_worker)
        registry.register(self.demo.research_worker)
        registry.register(self.demo.code_worker)
        return PlannerWorkerOrchestrator(planner, registry)

    def test_planner_routes_to_research_worker(self):
        stack = self._build_stack()
        decision, result, summary = stack.execute(
            task_id="t-1",
            intent="research and compare local backup options",
            action="remember",
        )
        self.assertEqual(decision.worker_name, "research_worker")
        self.assertEqual(result.worker_name, "research_worker")
        self.assertEqual(summary.status, "completed")

    def test_worker_result_contract_for_memory_store(self):
        stack = self._build_stack()
        _, result, _ = stack.execute(
            task_id="t-2",
            intent="remember local backups path is ./data/backups",
            action="remember",
        )
        self.assertEqual(result.status, "stored")
        self.assertIn("episode_id", result.output)
        self.assertIn("memory_recall", result.output)

    def test_summary_includes_worker_name_and_status(self):
        stack = self._build_stack()
        _, result, summary = stack.execute(
            task_id="t-3",
            intent="write code to parse logs",
            action="remember",
        )
        self.assertEqual(result.worker_name, "code_worker")
        self.assertIn("code_worker completed", summary.summary_text)

    def test_reject_unknown_worker_path(self):
        registry = WorkerRegistry()
        with self.assertRaises(KeyError):
            registry.get("unknown_worker")


if __name__ == "__main__":
    unittest.main()
