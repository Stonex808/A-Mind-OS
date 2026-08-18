"""Canonical harness domain contracts for A-Mind.

These records implement the typed boundary from the 2026-08-14 Harness Evolution
Governance Specification. They describe state; they do not grant authority.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HarnessLifecycle(str, Enum):
    DRAFT = "DRAFT"
    SCHEMA_VALID = "SCHEMA_VALID"
    SANDBOXED = "SANDBOXED"
    DEV_EVALUATED = "DEV_EVALUATED"
    VALIDATION_SELECTED = "VALIDATION_SELECTED"
    HELDOUT_EVALUATED = "HELDOUT_EVALUATED"
    STONE_REVIEW = "STONE_REVIEW"
    APPROVED = "APPROVED"
    SHADOW_ACTIVE = "SHADOW_ACTIVE"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    QUARANTINED = "QUARANTINED"
    ROLLED_BACK = "ROLLED_BACK"
    ARCHIVED = "ARCHIVED"


@dataclass(frozen=True)
class HarnessVersion:
    harness_version_id: str
    project_id: str
    parent_version_ids: tuple[str, ...]
    model_profile_id: str
    model_digest: str
    surface_manifest: dict[str, str]
    governance_anchor_hash: str
    artifact_hash: str
    created_by: str
    delegation_envelope_id: str | None
    created_at: str
    lifecycle_state: HarnessLifecycle
    rollback_pointer_id: str


@dataclass(frozen=True)
class HarnessDelta:
    harness_delta_id: str
    base_version_id: str
    failure_hypothesis: str
    typed_changes: tuple[dict[str, Any], ...]
    declared_blast_radius: dict[str, Any]
    capability_delta: dict[str, Any]
    protected_surface_assertion: dict[str, Any]
    expected_benefit: dict[str, Any]
    risk_class: str
    evaluation_contract_id: str
    reverse_patch_hash: str
    content_hash: str


@dataclass(frozen=True)
class EvaluationContract:
    evaluation_contract_id: str
    evaluator_version: str
    dataset_version: str
    development_split_id: str
    selection_split_commitment: str
    heldout_split_commitment: str
    hard_gates: tuple[str, ...]
    quality_metrics: tuple[str, ...]
    baselines: tuple[str, ...]
    budget_ledger: dict[str, int]
    seeds_and_repetitions: dict[str, Any]
    selection_rule: str
    tie_breakers: tuple[str, ...]
    stop_conditions: tuple[str, ...]
    isolation_attestation: str


@dataclass(frozen=True)
class PromotionReceipt:
    promotion_receipt_id: str
    candidate_version_id: str
    base_version_id: str
    evaluation_contract_id: str
    trace_bundle_hashes: tuple[str, ...]
    gate_results: tuple[dict[str, Any], ...]
    baseline_comparison: dict[str, Any]
    resource_actuals: dict[str, Any]
    evaluator_attestation: str
    stone_decision_id: str | None
    activation_scope: dict[str, Any]
    shadow_window: dict[str, Any]
    rollback_pointer_id: str


@dataclass(frozen=True)
class RollbackPointer:
    rollback_pointer_id: str
    from_version_id: str
    to_version_id: str
    artifact_snapshot_hash: str
    state_compatibility_rule: str
    inverse_migration_hash: str | None
    automatic_triggers: tuple[str, ...]
    manual_authority: tuple[str, ...] = field(default_factory=lambda: ("STONE",))
    rollback_test_receipt: str = ""
