"""Native A-Mind Harness runtime seams extracted from Refocus-OS ancestry.

This module deliberately keeps authority deterministic and side effects behind a
broker. It preserves useful Process Manager, Tool Registry, and Compute Economist
interfaces without carrying forward legacy shell execution or unrestricted file IO.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable


class AdmissionError(PermissionError):
    pass


class BudgetError(RuntimeError):
    pass


class AgentHealth(str, Enum):
    STARTING = "STARTING"
    IDLE = "IDLE"
    BUSY = "BUSY"
    STALE = "STALE"
    STOPPED = "STOPPED"


@dataclass(frozen=True)
class AdmissionDecision:
    admission_id: str
    actor_id: str
    intent_id: str
    action: str
    target: str
    argument_digest: str
    expires_at: datetime
    delegation_envelope_id: str | None = None
    allowed: bool = False
    obligations: tuple[str, ...] = ("audit",)

    def assert_valid_for(self, *, action: str, target: str, argument_digest: str) -> None:
        now = datetime.now(timezone.utc)
        if not self.allowed:
            raise AdmissionError("admission denied")
        if self.expires_at.tzinfo is None:
            raise AdmissionError("admission expiry must be timezone-aware")
        if now >= self.expires_at:
            raise AdmissionError("admission expired")
        if (self.action, self.target, self.argument_digest) != (action, target, argument_digest):
            raise AdmissionError("admission scope mismatch")


@dataclass(frozen=True)
class ResourceBudget:
    max_tokens: int
    max_wall_time_ms: int
    max_tool_calls: int
    max_worker_slots: int = 1


@dataclass
class ResourceUsage:
    tokens: int = 0
    wall_time_ms: int = 0
    tool_calls: int = 0
    worker_slots: int = 0


class ComputeEconomist:
    """Fail-closed budget accountant for deterministic scheduling decisions."""

    def __init__(self, budget: ResourceBudget) -> None:
        self.budget = budget
        self.usage = ResourceUsage()

    def reserve(self, *, tokens: int = 0, wall_time_ms: int = 0, tool_calls: int = 0, worker_slots: int = 0) -> None:
        proposed = ResourceUsage(
            tokens=self.usage.tokens + tokens,
            wall_time_ms=self.usage.wall_time_ms + wall_time_ms,
            tool_calls=self.usage.tool_calls + tool_calls,
            worker_slots=self.usage.worker_slots + worker_slots,
        )
        limits = (
            (proposed.tokens, self.budget.max_tokens, "tokens"),
            (proposed.wall_time_ms, self.budget.max_wall_time_ms, "wall time"),
            (proposed.tool_calls, self.budget.max_tool_calls, "tool calls"),
            (proposed.worker_slots, self.budget.max_worker_slots, "worker slots"),
        )
        for actual, ceiling, name in limits:
            if actual < 0 or actual > ceiling:
                raise BudgetError(f"{name} budget exceeded: {actual}>{ceiling}")
        self.usage = proposed

    def release_worker_slots(self, count: int = 1) -> None:
        if count < 0 or count > self.usage.worker_slots:
            raise BudgetError("invalid worker-slot release")
        self.usage.worker_slots -= count


@dataclass
class AgentLease:
    agent_id: str
    role: str
    health: AgentHealth = AgentHealth.STARTING
    last_heartbeat: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class LifecycleSupervisor:
    """Tracks worker lifecycle independently of the eventual OS-process backend."""

    def __init__(self, heartbeat_timeout_seconds: int = 30) -> None:
        if heartbeat_timeout_seconds <= 0:
            raise ValueError("heartbeat timeout must be positive")
        self.heartbeat_timeout_seconds = heartbeat_timeout_seconds
        self._agents: dict[str, AgentLease] = {}

    def register(self, agent_id: str, role: str) -> AgentLease:
        if agent_id in self._agents and self._agents[agent_id].health != AgentHealth.STOPPED:
            raise ValueError(f"agent already registered: {agent_id}")
        lease = AgentLease(agent_id=agent_id, role=role, health=AgentHealth.IDLE)
        self._agents[agent_id] = lease
        return lease

    def heartbeat(self, agent_id: str, *, busy: bool = False) -> None:
        lease = self._require(agent_id)
        if lease.health == AgentHealth.STOPPED:
            raise RuntimeError("stopped agent cannot heartbeat")
        lease.last_heartbeat = datetime.now(timezone.utc)
        lease.health = AgentHealth.BUSY if busy else AgentHealth.IDLE

    def mark_stopped(self, agent_id: str) -> None:
        self._require(agent_id).health = AgentHealth.STOPPED

    def refresh_health(self, now: datetime | None = None) -> tuple[AgentLease, ...]:
        now = now or datetime.now(timezone.utc)
        for lease in self._agents.values():
            if lease.health == AgentHealth.STOPPED:
                continue
            age = (now - lease.last_heartbeat).total_seconds()
            if age > self.heartbeat_timeout_seconds:
                lease.health = AgentHealth.STALE
        return tuple(self._agents.values())

    def _require(self, agent_id: str) -> AgentLease:
        try:
            return self._agents[agent_id]
        except KeyError as exc:
            raise KeyError(f"unknown agent: {agent_id}") from exc


ToolCallable = Callable[..., Any]


class ToolBroker:
    """Registry + execution boundary. Registered callables are never shell strings."""

    def __init__(self) -> None:
        self._tools: dict[str, ToolCallable] = {}

    def register(self, name: str, tool: ToolCallable) -> None:
        if not name or not callable(tool):
            raise ValueError("tool name and callable are required")
        if name in self._tools:
            raise ValueError(f"tool already registered: {name}")
        self._tools[name] = tool

    def invoke(
        self,
        *,
        name: str,
        arguments: dict[str, Any],
        argument_digest: str,
        admission: AdmissionDecision,
        economist: ComputeEconomist,
    ) -> Any:
        if name not in self._tools:
            raise KeyError(f"unknown tool: {name}")
        admission.assert_valid_for(
            action="tool.invoke",
            target=name,
            argument_digest=argument_digest,
        )
        economist.reserve(tool_calls=1)
        return self._tools[name](**arguments)
