"""MATPO-lite planner/worker backbone for the local orchestrator.

This module intentionally keeps the planner and workers deterministic and
contract-driven. It does not pretend full RL training exists.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass(frozen=True)
class WorkerRequest:
    """Contract handed from planner to one worker."""

    task_id: str
    intent: str
    action: str
    context: dict[str, Any]
    budget: dict[str, int]


@dataclass(frozen=True)
class WorkerResult:
    """Contract returned by workers back to planner."""

    task_id: str
    worker_name: str
    status: str
    summary: str
    output: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PlannerDecision:
    task_id: str
    worker_name: str
    action: str
    reason: str
    budget: dict[str, int]


@dataclass(frozen=True)
class PlannerSummary:
    task_id: str
    status: str
    worker_name: str
    summary_text: str
    highlighted_outputs: dict[str, Any]


class Worker(Protocol):
    name: str

    def run(self, request: WorkerRequest) -> WorkerResult:
        ...


class WorkerRegistry:
    def __init__(self) -> None:
        self._workers: dict[str, Worker] = {}

    def register(self, worker: Worker) -> None:
        self._workers[worker.name] = worker

    def get(self, worker_name: str) -> Worker:
        if worker_name not in self._workers:
            raise KeyError(f"unknown worker: {worker_name}")
        return self._workers[worker_name]

    def run(self, worker_name: str, request: WorkerRequest) -> WorkerResult:
        worker = self.get(worker_name)
        return worker.run(request)


class LocalPlanner:
    """Simple planner that makes explicit, testable routing choices."""

    def plan(self, *, task_id: str, intent: str, action: str) -> PlannerDecision:
        lowered = intent.lower()
        if "recall" in lowered or action == "recall":
            worker_name = "memory_worker"
            reason = "Intent asks to recall context."
        elif any(token in lowered for token in ("research", "search", "investigate", "compare")):
            worker_name = "research_worker"
            reason = "Intent asks for research-style synthesis."
        elif any(token in lowered for token in ("code", "refactor", "python", "function", "bug")):
            worker_name = "code_worker"
            reason = "Intent asks for code-oriented work."
        else:
            worker_name = "memory_worker"
            reason = "Defaulted to memory worker for local persistence and recall."

        return PlannerDecision(
            task_id=task_id,
            worker_name=worker_name,
            action=action,
            reason=reason,
            budget={"token_budget": 600, "time_budget_ms": 1000, "max_context_items": 5},
        )

    def summarize(self, worker_result: WorkerResult) -> PlannerSummary:
        if worker_result.status == "failed":
            status = "failed"
            text = f"{worker_result.worker_name} failed: {'; '.join(worker_result.errors) or 'unknown error'}"
        else:
            status = "completed"
            text = f"{worker_result.worker_name} completed: {worker_result.summary}"

        highlighted = {
            "status": worker_result.status,
            "output_keys": sorted(worker_result.output.keys()),
        }
        return PlannerSummary(
            task_id=worker_result.task_id,
            status=status,
            worker_name=worker_result.worker_name,
            summary_text=text,
            highlighted_outputs=highlighted,
        )


class MemoryWorker:
    name = "memory_worker"

    def __init__(self, memory_interface: Any) -> None:
        self.memory = memory_interface

    def run(self, request: WorkerRequest) -> WorkerResult:
        try:
            if request.action == "recall":
                recall = self.memory.recall_for_situation(request.intent)
                return WorkerResult(
                    task_id=request.task_id,
                    worker_name=self.name,
                    status="recalled",
                    summary="Returned bounded recall context.",
                    output={"memory_recall": _bounded_recall(recall, request.budget.get("max_context_items", 5))},
                )

            topic = _extract_topic(request.intent)
            self.memory.learn_fact(topic, "noted_as", request.intent)
            episode_id = self.memory.remember_task(
                task=request.intent,
                actions=["planned task", "delegated to memory_worker", "stored local memory"],
                outcome="Stored locally for deterministic recall",
                success=True,
                observations=["local-first", "offline"],
                tags=["planner-worker", "memory"],
            )
            recall = self.memory.recall_for_situation(request.intent)
            return WorkerResult(
                task_id=request.task_id,
                worker_name=self.name,
                status="stored",
                summary="Stored intent and episode in local memory.",
                output={
                    "topic": topic,
                    "episode_id": episode_id,
                    "memory_recall": _bounded_recall(recall, request.budget.get("max_context_items", 5)),
                },
            )
        except Exception as exc:  # pragma: no cover - defensive boundary
            return WorkerResult(
                task_id=request.task_id,
                worker_name=self.name,
                status="failed",
                summary="Memory worker failed.",
                errors=[str(exc)],
            )


class ResearchWorker:
    name = "research_worker"

    def __init__(self, memory_interface: Any) -> None:
        self.memory = memory_interface

    def run(self, request: WorkerRequest) -> WorkerResult:
        recall = self.memory.recall_for_situation(request.intent)
        bounded = _bounded_recall(recall, request.budget.get("max_context_items", 5))
        facts = bounded.get("relevant_facts", [])
        summary = "Synthesized local memory context for research intent."
        return WorkerResult(
            task_id=request.task_id,
            worker_name=self.name,
            status="completed",
            summary=summary,
            output={
                "findings": [
                    "No network calls were made.",
                    f"Used {len(facts)} locally recalled fact(s) as source material.",
                ],
                "memory_recall": bounded,
            },
        )


class CodeWorker:
    name = "code_worker"

    def __init__(self, memory_interface: Any) -> None:
        self.memory = memory_interface

    def run(self, request: WorkerRequest) -> WorkerResult:
        recall = self.memory.recall_for_situation(request.intent)
        bounded = _bounded_recall(recall, request.budget.get("max_context_items", 5))
        return WorkerResult(
            task_id=request.task_id,
            worker_name=self.name,
            status="completed",
            summary="Produced a local code-task recommendation.",
            output={
                "recommendations": [
                    "Prefer contract-driven interfaces for planner and workers.",
                    "Keep worker contexts bounded to deterministic slices.",
                ],
                "memory_recall": bounded,
            },
        )


class PlannerWorkerOrchestrator:
    def __init__(self, planner: LocalPlanner, registry: WorkerRegistry) -> None:
        self.planner = planner
        self.registry = registry

    def execute(self, *, task_id: str, intent: str, action: str) -> tuple[PlannerDecision, WorkerResult, PlannerSummary]:
        decision = self.planner.plan(task_id=task_id, intent=intent, action=action)
        request = WorkerRequest(
            task_id=task_id,
            intent=intent,
            action=decision.action,
            context={"planner_reason": decision.reason},
            budget=decision.budget,
        )
        result = self.registry.run(decision.worker_name, request)
        summary = self.planner.summarize(result)
        return decision, result, summary


def _extract_topic(intent: str) -> str:
    lowered = intent.lower()
    for prefix in ("remember ", "store ", "note "):
        if lowered.startswith(prefix):
            return intent[len(prefix):].strip() or "intent"
    return "intent"


def _bounded_recall(recall: dict[str, Any], max_items: int) -> dict[str, Any]:
    bounded: dict[str, Any] = {}
    for key in ("past_experiences", "relevant_facts", "procedural_memories"):
        value = recall.get(key, [])
        bounded[key] = value[:max_items] if isinstance(value, list) else []
    return bounded
