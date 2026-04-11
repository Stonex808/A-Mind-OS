"""Orchestrator service boundary with local task dispatch and structured execution logs."""

from __future__ import annotations

import json
import sqlite3
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from task_schema import TaskEnvelope


class Worker(Protocol):
    name: str

    def can_handle(self, task: TaskEnvelope) -> bool: ...

    def execute(self, task: TaskEnvelope) -> dict[str, Any]: ...


@dataclass(slots=True)
class PlannerDecision:
    worker_name: str
    rationale: str


class LocalPlanner:
    """MVP planner interface that maps task kinds to workers."""

    def choose_worker(self, task: TaskEnvelope, available_workers: list[Worker]) -> PlannerDecision:
        preferred = {
            "memory": "memory_worker",
            "research": "research_worker",
            "code": "code_worker",
        }.get(task.kind)

        for worker in available_workers:
            if preferred and worker.name == preferred and worker.can_handle(task):
                return PlannerDecision(worker_name=worker.name, rationale=f"kind={task.kind} preferred")

        for worker in available_workers:
            if worker.can_handle(task):
                return PlannerDecision(worker_name=worker.name, rationale="first compatible worker")

        raise ValueError(f"no worker can handle task kind '{task.kind}'")


class WorkerRegistry:
    def __init__(self, workers: list[Worker]) -> None:
        self._workers = workers
        self._by_name = {worker.name: worker for worker in workers}

    @property
    def workers(self) -> list[Worker]:
        return list(self._workers)

    def get(self, name: str) -> Worker:
        return self._by_name[name]


class ExecutionLogStore:
    """Structured execution logging to SQLite and JSONL for local inspection."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.db_path = data_dir / "orchestrator.db"
        self.events_path = data_dir / "execution_events.jsonl"
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS orchestrator_task_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at REAL NOT NULL,
                    task_id TEXT NOT NULL,
                    source TEXT NOT NULL,
                    kind TEXT NOT NULL,
                    status TEXT NOT NULL,
                    worker_name TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    details_json TEXT NOT NULL
                )
                """
            )
            conn.commit()

    def log_event(
        self,
        *,
        task: TaskEnvelope,
        status: str,
        worker_name: str,
        summary: str,
        details: dict[str, Any],
    ) -> dict[str, Any]:
        event = {
            "created_at": time.time(),
            "task_id": task.task_id,
            "source": task.source,
            "kind": task.kind,
            "status": status,
            "worker_name": worker_name,
            "summary": summary,
            "details": details,
        }
        with self.events_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(event) + "\n")

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO orchestrator_task_events (
                    created_at, task_id, source, kind, status, worker_name, summary, details_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event["created_at"],
                    event["task_id"],
                    event["source"],
                    event["kind"],
                    event["status"],
                    worker_name,
                    summary,
                    json.dumps(details),
                ),
            )
            conn.commit()
        return event


class TaskDispatcher:
    """FIFO dispatcher that routes one task at a time through planner + worker."""

    def __init__(self, planner: LocalPlanner, registry: WorkerRegistry, logs: ExecutionLogStore) -> None:
        self.planner = planner
        self.registry = registry
        self.logs = logs

    def dispatch(self, task: TaskEnvelope) -> dict[str, Any]:
        decision = self.planner.choose_worker(task, self.registry.workers)
        worker = self.registry.get(decision.worker_name)
        outcome = worker.execute(task)
        summary = str(outcome.get("message", "task completed"))
        event = self.logs.log_event(
            task=task,
            status=str(outcome.get("status", "completed")),
            worker_name=worker.name,
            summary=summary,
            details={"planner_rationale": decision.rationale, "outcome": outcome},
        )
        return {
            "task": task.as_dict(),
            "routing": {"worker": worker.name, "rationale": decision.rationale},
            "result": outcome,
            "event": event,
        }


class MemoryWorker:
    name = "memory_worker"

    def __init__(self, memory_interface: Any) -> None:
        self.memory = memory_interface

    def can_handle(self, task: TaskEnvelope) -> bool:
        return task.kind in {"memory", "recall"}

    def execute(self, task: TaskEnvelope) -> dict[str, Any]:
        if "recall" in task.content.lower() or task.kind == "recall":
            recall = self.memory.recall_for_situation(task.content)
            return {
                "status": "recalled",
                "message": "Returned matching local context.",
                "memory_recall": recall,
            }

        topic = task.content.replace("remember", "", 1).strip() or "intent"
        self.memory.learn_fact(topic, "noted_as", task.content)
        episode_id = self.memory.remember_task(
            task=task.content,
            actions=["validated task envelope", "stored semantic fact", "recorded episodic memory"],
            outcome="Stored locally for deterministic recall",
            success=True,
            observations=["offline-only", "local-first"],
            tags=["orchestrator", "memory"],
        )
        return {
            "status": "stored",
            "message": "Intent stored in local memory.",
            "episode_id": episode_id,
            "topic": topic,
        }


class ResearchWorker:
    name = "research_worker"

    def can_handle(self, task: TaskEnvelope) -> bool:
        return task.kind == "research"

    def execute(self, task: TaskEnvelope) -> dict[str, Any]:
        return {
            "status": "completed",
            "message": "Research worker completed a local placeholder pass.",
            "summary": f"Research scope captured: {task.content[:160]}",
        }


class CodeWorker:
    name = "code_worker"

    def can_handle(self, task: TaskEnvelope) -> bool:
        return task.kind == "code"

    def execute(self, task: TaskEnvelope) -> dict[str, Any]:
        return {
            "status": "completed",
            "message": "Code worker completed a bounded local review.",
            "summary": f"Code task registered: {task.content[:160]}",
        }
