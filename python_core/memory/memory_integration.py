"""Local-first semantic, episodic, and procedural memory integration."""

from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Optional

from ..refocus_core.logging import setup_logging
from ..refocus_core.persistence import (
    load_memory_persistence_settings,
    sanitize_for_local_persistence,
)
from .episodic import Episode, EpisodicMemory
from .procedural import ProceduralMemory
from .semantic import Concept, Fact, SemanticMemory

logger = setup_logging("memory-integration", level="WARNING")
_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    temporary.replace(path)


class LocalSemanticMemory:
    """Small JSON-backed semantic store used by the default offline path."""

    def __init__(self, persist_directory: str | Path, sensitive_content_mode: str = "redact") -> None:
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.sensitive_content_mode = sensitive_content_mode
        self.facts_path = self.persist_dir / "facts.json"
        self.concepts_path = self.persist_dir / "concepts.json"
        self.facts = self._load(self.facts_path, Fact)
        self.concepts = self._load(self.concepts_path, Concept)

    def store_fact(self, fact: Fact) -> str:
        clean = Fact(**sanitize_for_local_persistence(asdict(fact), self.sensitive_content_mode))
        for existing in self.facts:
            if (existing.subject, existing.predicate, existing.object) == (
                clean.subject,
                clean.predicate,
                clean.object,
            ):
                return existing.id or ""
        clean.id = clean.id or str(uuid.uuid4())
        clean.timestamp = clean.timestamp or time.time()
        self.facts.append(clean)
        _write_json(self.facts_path, [asdict(item) for item in self.facts])
        return clean.id

    def store_concept(self, concept: Concept) -> str:
        clean = Concept(**sanitize_for_local_persistence(asdict(concept), self.sensitive_content_mode))
        for existing in self.concepts:
            if (existing.name, existing.definition) == (clean.name, clean.definition):
                return existing.id or ""
        clean.id = clean.id or str(uuid.uuid4())
        self.concepts.append(clean)
        _write_json(self.concepts_path, [asdict(item) for item in self.concepts])
        return clean.id

    def query_facts(self, query: str, n_results: int = 5) -> list[Fact]:
        scored = sorted(
            ((self._score(query, f"{item.subject} {item.predicate} {item.object}"), item) for item in self.facts),
            key=lambda pair: pair[0],
            reverse=True,
        )
        return [item for score, item in scored[:n_results] if score]

    def query_concepts(self, query: str, n_results: int = 3) -> list[Concept]:
        scored = sorted(
            ((self._score(query, f"{item.name} {item.definition}"), item) for item in self.concepts),
            key=lambda pair: pair[0],
            reverse=True,
        )
        return [item for score, item in scored[:n_results] if score]

    def learn_from_text(self, text: str, source: str = "learned") -> None:
        for sentence in (part.strip() for part in text.split(".")):
            if " is " not in sentence:
                continue
            subject, value = sentence.split(" is ", 1)
            self.store_fact(Fact(None, subject.strip(), "is", value.strip(), 0.8, source, time.time()))

    def get_statistics(self) -> dict[str, Any]:
        return {"total_facts": len(self.facts), "total_concepts": len(self.concepts), "backend": "json-local"}

    @staticmethod
    def _load(path: Path, model: type[Any]) -> list[Any]:
        if not path.exists():
            return []
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, list):
            raise ValueError(f"{path} must contain a JSON array")
        return [model(**item) for item in payload]

    @staticmethod
    def _score(query: str, candidate: str) -> int:
        return len(set(_TOKEN_RE.findall(query.lower())) & set(_TOKEN_RE.findall(candidate.lower())))


class LocalEpisodicMemory:
    """JSON-backed episodic store with deterministic token-overlap recall."""

    def __init__(self, persist_directory: str | Path, sensitive_content_mode: str = "redact") -> None:
        self.persist_dir = Path(persist_directory)
        self.episodes_store = self.persist_dir / "episodes"
        self.episodes_store.mkdir(parents=True, exist_ok=True)
        self.sensitive_content_mode = sensitive_content_mode

    def has_episode(self, episode_id: Optional[str]) -> bool:
        return bool(episode_id and (self.episodes_store / f"{episode_id}.json").exists())

    def store_episode(self, episode: Episode) -> str:
        clean = Episode(**sanitize_for_local_persistence(asdict(episode), self.sensitive_content_mode))
        clean.id = clean.id or str(uuid.uuid4())
        _write_json(self.episodes_store / f"{clean.id}.json", asdict(clean))
        episode.id = clean.id
        return clean.id

    def retrieve_similar(
        self,
        query: str,
        agent_id: str,
        n_results: int = 3,
        success_only: bool = False,
    ) -> list[Episode]:
        matches: list[tuple[int, Episode]] = []
        for path in self.episodes_store.glob("*.json"):
            episode = Episode(**json.loads(path.read_text(encoding="utf-8")))
            if episode.agent_id != agent_id or (success_only and not episode.success):
                continue
            candidate = " ".join([episode.task, episode.outcome, *episode.actions, *episode.observations])
            score = LocalSemanticMemory._score(query, candidate)
            if score:
                matches.append((score, episode))
        matches.sort(key=lambda pair: (pair[0], pair[1].timestamp), reverse=True)
        return [episode for _, episode in matches[:n_results]]

    def get_statistics(self, agent_id: Optional[str] = None) -> dict[str, Any]:
        payloads = [json.loads(path.read_text(encoding="utf-8")) for path in self.episodes_store.glob("*.json")]
        if agent_id is not None:
            payloads = [item for item in payloads if item.get("agent_id") == agent_id]
        successes = sum(bool(item.get("success")) for item in payloads)
        total = len(payloads)
        return {
            "total_episodes": total,
            "successful": successes,
            "failed": total - successes,
            "success_rate": successes / total if total else 0.0,
            "backend": "json-local",
        }


class ArtHippoNet:
    """Combined memory stack with optional local vector backends."""

    def __init__(
        self,
        agent_id: str,
        prefer_local_fallback: bool = False,
        memory_root: str | Path | None = None,
        sensitive_content_mode: str | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.settings = load_memory_persistence_settings(
            memory_root=memory_root,
            sensitive_content_mode=sensitive_content_mode,
        )
        self.episodic, self.semantic = self._build_backends(prefer_local_fallback)
        self.procedural = ProceduralMemory(
            self.settings.procedural_dir,
            sensitive_content_mode=self.settings.sensitive_content_mode,
        )

    def _build_backends(self, prefer_local: bool) -> tuple[Any, Any]:
        if not prefer_local:
            try:
                return (
                    EpisodicMemory(str(self.settings.episodic_dir)),
                    SemanticMemory(str(self.settings.semantic_dir)),
                )
            except ModuleNotFoundError:
                logger.info("vector_memory_unavailable_using_local_fallback")
        return (
            LocalEpisodicMemory(self.settings.episodic_dir, self.settings.sensitive_content_mode),
            LocalSemanticMemory(self.settings.semantic_dir, self.settings.sensitive_content_mode),
        )

    def integrated_recall(self, situation: str) -> dict[str, Any]:
        episodes = self.episodic.retrieve_similar(situation, self.agent_id, n_results=3)
        facts = self.semantic.query_facts(situation, n_results=5)
        concepts = self.semantic.query_concepts(situation, n_results=3)
        procedures = self.procedural.retrieve_by_description(situation, n_results=3)
        return {
            "situation": situation,
            "past_experiences": [
                {"task": item.task, "outcome": item.outcome, "success": item.success} for item in episodes
            ],
            "relevant_facts": [f"{item.subject} {item.predicate} {item.object}" for item in facts],
            "relevant_concepts": [
                {"name": item.name, "definition": item.definition} for item in concepts
            ],
            "applicable_procedures": [
                {"name": item.name, "description": item.description, "steps": len(item.steps)}
                for item in procedures
            ],
        }

    def learn_from_success(self, episode: Episode) -> str:
        if not getattr(self.episodic, "has_episode", lambda _id: False)(episode.id):
            self.episodic.store_episode(episode)
        if episode.success and len(episode.actions) >= 2:
            name = f"procedure_from_{episode.id[:8]}"
            if self.procedural.retrieve_by_name(name) is None:
                self.procedural.extract_procedure_from_episode(
                    {"actions": episode.actions, "tags": episode.tags or []},
                    name,
                    f"Learned from: {episode.task}",
                )
        return episode.id or ""

    def get_complete_stats(self) -> dict[str, Any]:
        return {
            "episodic": self.episodic.get_statistics(self.agent_id),
            "semantic": self.semantic.get_statistics(),
            "procedural": self.procedural.get_statistics(),
        }


class CompleteAgentMemoryInterface:
    """Public memory API that sanitizes content before any backend sees it."""

    def __init__(
        self,
        agent_id: str,
        prefer_local_fallback: bool = False,
        memory_root: str | Path | None = None,
        sensitive_content_mode: str | None = None,
    ) -> None:
        self.agent_id = agent_id
        self.memory = ArtHippoNet(
            agent_id,
            prefer_local_fallback=prefer_local_fallback,
            memory_root=memory_root,
            sensitive_content_mode=sensitive_content_mode,
        )
        self.sensitive_content_mode = self.memory.settings.sensitive_content_mode

    def _clean(self, value: Any) -> Any:
        return sanitize_for_local_persistence(value, self.sensitive_content_mode)

    def remember_task(
        self,
        task: str,
        actions: list[str],
        outcome: str,
        success: bool = True,
        observations: Optional[list[str]] = None,
        tags: Optional[list[str]] = None,
    ) -> str:
        payload = self._clean(
            {
                "task": task,
                "actions": actions,
                "outcome": outcome,
                "observations": observations or [],
                "tags": tags or [],
            }
        )
        episode = Episode(
            id=None,
            agent_id=self.agent_id,
            timestamp=time.time(),
            task=payload["task"],
            actions=payload["actions"],
            observations=payload["observations"],
            outcome=payload["outcome"],
            success=success,
            reward=1.0 if success else 0.0,
            tags=payload["tags"],
        )
        return self.memory.learn_from_success(episode)

    def recall_for_situation(self, situation: str) -> dict[str, Any]:
        return self.memory.integrated_recall(self._clean(situation))

    def learn_fact(
        self,
        subject: str,
        predicate: str,
        value: str,
        confidence: float = 1.0,
        source: str = "agent",
    ) -> str:
        payload = self._clean({"subject": subject, "predicate": predicate, "object": value, "source": source})
        return self.memory.semantic.store_fact(
            Fact(None, payload["subject"], payload["predicate"], payload["object"], confidence, payload["source"], time.time())
        )

    def define_concept(
        self,
        name: str,
        definition: str,
        category: str,
        related_concepts: Optional[list[str]] = None,
        examples: Optional[list[str]] = None,
    ) -> str:
        payload = self._clean(
            {
                "name": name,
                "definition": definition,
                "category": category,
                "related_concepts": related_concepts or [],
                "examples": examples or [],
            }
        )
        return self.memory.semantic.store_concept(Concept(id=None, **payload))

    def get_stats(self) -> dict[str, Any]:
        return self.memory.get_complete_stats()


__all__ = [
    "ArtHippoNet",
    "CompleteAgentMemoryInterface",
    "LocalEpisodicMemory",
    "LocalSemanticMemory",
]
