"""Fail-closed surface registry for the A-Mind Harness constitutional boundary."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class SurfaceClass(str, Enum):
    PROTECTED = "protected"
    EVOLVABLE = "evolvable"
    CONDITIONAL = "conditional"


PROTECTED_SURFACES = frozenset({
    "I0.root_authority",
    "I1.governance",
    "I2.capability_safety",
    "I3.evidence_integrity",
    "I4.evaluation_integrity",
    "I5.promotion_control",
    "I6.trust_roots",
})

EVOLVABLE_SURFACES = frozenset({
    "M1.prompting",
    "M2.context_composition",
    "M3.tool_policy",
    "M4.control_flow",
    "M5.skills",
    "M6.provider_profile",
    "M7.delegation_topology",
    "M8.reversible_runtime_heuristics",
})

CONDITIONAL_SURFACES = frozenset({
    "tool_implementation",
    "database_schema",
    "api_contract",
    "memory_mutation_policy",
    "evaluator_logic",
    "model_weights",
    "constitutional_governance",
    "model_succession_policy",
    "cross_model_state_transfer",
    "consolidation_mutation_policy",
})


@dataclass(frozen=True)
class SurfaceDecision:
    surface_id: str
    classification: SurfaceClass
    candidate_mutation_allowed: bool
    reason: str


def classify_surface(surface_id: str) -> SurfaceDecision:
    if surface_id in PROTECTED_SURFACES:
        return SurfaceDecision(surface_id, SurfaceClass.PROTECTED, False, "runtime-immutable constitutional surface")
    if surface_id in EVOLVABLE_SURFACES:
        return SurfaceDecision(surface_id, SurfaceClass.EVOLVABLE, True, "versioned harness userland surface")
    if surface_id in CONDITIONAL_SURFACES:
        return SurfaceDecision(surface_id, SurfaceClass.CONDITIONAL, False, "separate gated change class")
    return SurfaceDecision(surface_id, SurfaceClass.PROTECTED, False, "unknown surfaces default to protected")


def assert_candidate_mutation_allowed(surface_id: str) -> None:
    decision = classify_surface(surface_id)
    if not decision.candidate_mutation_allowed:
        raise PermissionError(f"candidate mutation denied for {surface_id}: {decision.reason}")
