"""Procedural memory storing learned skills and procedures."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..refocus_core.logging import setup_logging

MEMORY_ROOT = Path(__file__).resolve().parents[2] / "data" / "memory"
logger = setup_logging("procedural-memory")


@dataclass
class ActionStep:
    """Single step within a procedure."""

    action: str
    parameters: Dict[str, Any]
    expected_outcome: str


@dataclass
class Procedure:
    """Stored procedure (sequence of steps)."""

    id: Optional[str]
    name: str
    description: str
    steps: List[ActionStep]
    success_count: int = 0
    failure_count: int = 0
    avg_execution_time: float = 0.0
    preconditions: Optional[List[str]] = field(default_factory=list)
    postconditions: Optional[List[str]] = field(default_factory=list)
    tags: Optional[List[str]] = field(default_factory=list)


class ProceduralMemory:
    """Persistent storage for procedures."""

    def __init__(self, persist_directory: str | Path | None = None) -> None:
        self.persist_dir = Path(persist_directory) if persist_directory is not None else MEMORY_ROOT / "procedural"
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.procedures: Dict[str, Procedure] = {}
        self._load_procedures()
        logger.info("procedural_memory_initialized", extra={"persist_directory": str(self.persist_dir)})

    def store_procedure(self, procedure: Procedure) -> str:
        if not procedure.id:
            procedure.id = str(uuid.uuid4())
        self.procedures[procedure.id] = procedure
        self._save_procedure(procedure)
        logger.debug("procedure_stored", extra={"procedure_id": procedure.id, "name": procedure.name})
        return procedure.id

    def retrieve_by_name(self, name: str) -> Optional[Procedure]:
        for procedure in self.procedures.values():
            if procedure.name == name:
                return procedure
        return None

    def retrieve_by_description(self, description: str, n_results: int = 5) -> List[Procedure]:
        query_words = set(description.lower().split())
        matches: List[tuple[int, Procedure]] = []
        for procedure in self.procedures.values():
            proc_words = set(procedure.description.lower().split())
            overlap = len(query_words & proc_words)
            if overlap:
                matches.append((overlap, procedure))
        matches.sort(key=lambda item: item[0], reverse=True)
        return [procedure for _, procedure in matches[:n_results]]

    def retrieve_by_tags(self, tags: List[str]) -> List[Procedure]:
        desired = set(tags)
        return [proc for proc in self.procedures.values() if proc.tags and desired & set(proc.tags)]

    def execute_procedure(self, procedure_id: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        procedure = self.procedures.get(procedure_id)
        if not procedure:
            raise ValueError(f"Procedure {procedure_id} not found")

        plan: List[Dict[str, Any]] = []
        for step in procedure.steps:
            plan.append(
                {
                    "action": step.action,
                    "parameters": step.parameters,
                    "expected_outcome": step.expected_outcome,
                }
            )
        logger.info("procedure_retrieved", extra={"procedure": procedure.name, "steps": len(plan)})
        return plan

    def record_execution(self, procedure_id: str, success: bool, execution_time: float) -> None:
        procedure = self.procedures.get(procedure_id)
        if not procedure:
            return
        if success:
            procedure.success_count += 1
        else:
            procedure.failure_count += 1
        total = procedure.success_count + procedure.failure_count
        procedure.avg_execution_time = (
            (procedure.avg_execution_time * (total - 1) + execution_time) / total
            if total
            else execution_time
        )
        self._save_procedure(procedure)
        logger.debug(
            "procedure_execution_recorded",
            extra={
                "procedure": procedure.name,
                "success": success,
                "total_runs": total,
            },
        )

    def extract_procedure_from_episode(self, episode_data: Dict[str, Any], name: str, description: str) -> str:
        steps = [
            ActionStep(action=action, parameters={}, expected_outcome="")
            for action in episode_data.get("actions", [])
        ]
        procedure = Procedure(
            id=None,
            name=name,
            description=description,
            steps=steps,
            success_count=1,
            tags=episode_data.get("tags", []),
        )
        return self.store_procedure(procedure)

    def get_statistics(self) -> Dict[str, Any]:
        total = len(self.procedures)
        if not total:
            return {"total_procedures": 0}
        successes = sum(proc.success_count for proc in self.procedures.values())
        failures = sum(proc.failure_count for proc in self.procedures.values())
        executions = successes + failures
        success_rate = successes / executions if executions else 0.0
        return {
            "total_procedures": total,
            "total_executions": executions,
            "total_successes": successes,
            "overall_success_rate": success_rate,
        }

    def _save_procedure(self, procedure: Procedure) -> None:
        path = self.persist_dir / f"{procedure.id}.json"
        payload = asdict(procedure)
        payload["steps"] = [asdict(step) for step in procedure.steps]
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2)

    def _load_procedures(self) -> None:
        if not self.persist_dir.exists():
            return
        for path in self.persist_dir.glob("*.json"):
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            steps = [ActionStep(**step) for step in data.get("steps", [])]
            data["steps"] = steps
            procedure = Procedure(**data)
            self.procedures[procedure.id] = procedure
        logger.info("procedures_loaded", extra={"count": len(self.procedures)})


def seed_common_procedures(memory: ProceduralMemory) -> None:
    """Seed procedural memory with common programming workflows."""

    procedures = [
        Procedure(
            id=None,
            name="read_file",
            description="Read contents of a text file",
            steps=[
                ActionStep("open_file", {"mode": "r"}, "File handle obtained"),
                ActionStep("read_contents", {}, "Contents read into memory"),
                ActionStep("close_file", {}, "File handle closed"),
            ],
            tags=["file", "io", "read"],
        ),
        Procedure(
            id=None,
            name="sort_list",
            description="Sort a list of items",
            steps=[
                ActionStep("check_list_type", {}, "List type verified"),
                ActionStep("apply_sort", {"algorithm": "quicksort"}, "List sorted"),
                ActionStep("return_result", {}, "Sorted list returned"),
            ],
            tags=["sorting", "list", "algorithm"],
        ),
        Procedure(
            id=None,
            name="web_request",
            description="Make an HTTP request and parse response",
            steps=[
                ActionStep("import_requests", {}, "Requests library loaded"),
                ActionStep("make_request", {"method": "GET"}, "HTTP request sent"),
                ActionStep("check_status", {}, "Status code verified"),
                ActionStep("parse_response", {}, "Response parsed"),
            ],
            tags=["web", "http", "api"],
        ),
    ]
    for procedure in procedures:
        memory.store_procedure(procedure)
    logger.info("common_procedures_seeded")


__all__ = ["ProceduralMemory", "Procedure", "ActionStep", "seed_common_procedures"]
