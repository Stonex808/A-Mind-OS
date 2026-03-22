"""Integrated ArtHippoNet memory system with local-first fallbacks."""

from __future__ import annotations

import json
import re
import time
import uuid
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from refocus_core.logging import setup_logging

from .episodic import Episode, EpisodicMemory
from .procedural import ProceduralMemory, Procedure
from .semantic import Concept, Fact, SemanticMemory

logger = setup_logging("memory-integration")

_TOKEN_RE = re.compile(r"[a-z0-9]+")


class LocalSemanticMemory:
    """JSON-backed semantic fallback that avoids optional vector dependencies."""

    def __init__(self, persist_directory: str = "./data/memory/semantic_local") -> None:
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.facts_path = self.persist_dir / "facts.json"
        self.concepts_path = self.persist_dir / "concepts.json"
        self.facts: List[Fact] = self._load_facts()
        self.concepts: List[Concept] = self._load_concepts()
        logger.info("local_semantic_memory_initialized", extra={"persist_directory": str(self.persist_dir)})

    def store_fact(self, fact: Fact) -> str:
        for existing in self.facts:
            if (existing.subject, existing.predicate, existing.object) == (fact.subject, fact.predicate, fact.object):
                return existing.id or ""
        if not fact.id:
            fact.id = str(uuid.uuid4())
        if not fact.timestamp:
            fact.timestamp = time.time()
        self.facts.append(fact)
        self._save_facts()
        return fact.id

    def store_concept(self, concept: Concept) -> str:
        for existing in self.concepts:
            if existing.name == concept.name and existing.definition == concept.definition:
                return existing.id or ""
        if not concept.id:
            concept.id = str(uuid.uuid4())
        self.concepts.append(concept)
        self._save_concepts()
        return concept.id

    def query_facts(self, query: str, n_results: int = 5) -> List[Fact]:
        scored = sorted(
            ((self._score_text(query, f"{fact.subject} {fact.predicate} {fact.object}"), fact) for fact in self.facts),
            key=lambda item: item[0],
            reverse=True,
        )
        return [fact for score, fact in scored[:n_results] if score > 0]

    def query_concepts(self, query: str, n_results: int = 3) -> List[Concept]:
        scored = sorted(
            ((self._score_text(query, f"{concept.name} {concept.definition}"), concept) for concept in self.concepts),
            key=lambda item: item[0],
            reverse=True,
        )
        return [concept for score, concept in scored[:n_results] if score > 0]

    def learn_from_text(self, text: str, source: str = "learned") -> None:
        for sentence in [segment.strip() for segment in text.split(".") if segment.strip()]:
            if " is " not in sentence:
                continue
            subject, remainder = sentence.split(" is ", 1)
            self.store_fact(
                Fact(
                    id=None,
                    subject=subject.strip(),
                    predicate="is",
                    object=remainder.strip(),
                    confidence=0.8,
                    source=source,
                    timestamp=time.time(),
                )
            )

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_facts": len(self.facts),
            "total_concepts": len(self.concepts),
            "backend": "json-local",
        }

    def _load_facts(self) -> List[Fact]:
        if not self.facts_path.exists():
            return []
        with open(self.facts_path, "r", encoding="utf-8") as handle:
            return [Fact(**item) for item in json.load(handle)]

    def _save_facts(self) -> None:
        with open(self.facts_path, "w", encoding="utf-8") as handle:
            json.dump([asdict(fact) for fact in self.facts], handle, indent=2)

    def _load_concepts(self) -> List[Concept]:
        if not self.concepts_path.exists():
            return []
        with open(self.concepts_path, "r", encoding="utf-8") as handle:
            return [Concept(**item) for item in json.load(handle)]

    def _save_concepts(self) -> None:
        with open(self.concepts_path, "w", encoding="utf-8") as handle:
            json.dump([asdict(concept) for concept in self.concepts], handle, indent=2)

    @staticmethod
    def _score_text(query: str, candidate: str) -> int:
        query_tokens = set(_TOKEN_RE.findall(query.lower()))
        candidate_tokens = set(_TOKEN_RE.findall(candidate.lower()))
        return len(query_tokens & candidate_tokens)


class LocalEpisodicMemory:
    """JSON-backed episodic fallback that uses token overlap for recall."""

    def __init__(self, persist_directory: str = "./data/memory/episodic_local") -> None:
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self.episodes_store = self.persist_dir / "episodes"
        self.episodes_store.mkdir(parents=True, exist_ok=True)
        logger.info("local_episodic_memory_initialized", extra={"persist_directory": str(self.persist_dir)})

    def store_episode(self, episode: Episode) -> str:
        if not episode.id:
            episode.id = str(uuid.uuid4())
        path = self.episodes_store / f"{episode.id}.json"
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(asdict(episode), handle, indent=2)
        return episode.id

    def retrieve_similar(
        self,
        query: str,
        agent_id: str,
        n_results: int = 3,
        success_only: bool = False,
    ) -> List[Episode]:
        matches: List[tuple[int, Episode]] = []
        for path in self.episodes_store.glob("*.json"):
            with open(path, "r", encoding="utf-8") as handle:
                episode = Episode(**json.load(handle))
            if episode.agent_id != agent_id:
                continue
            if success_only and not episode.success:
                continue
            search_text = " ".join([episode.task, episode.outcome, *episode.actions, *episode.observations])
            score = LocalSemanticMemory._score_text(query, search_text)
            if score > 0:
                matches.append((score, episode))
        matches.sort(key=lambda item: (item[0], item[1].timestamp), reverse=True)
        return [episode for _, episode in matches[:n_results]]

    def get_statistics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        episodes = []
        for path in self.episodes_store.glob("*.json"):
            with open(path, "r", encoding="utf-8") as handle:
                episodes.append(json.load(handle))
        if agent_id is not None:
            episodes = [episode for episode in episodes if episode.get("agent_id") == agent_id]
        total = len(episodes)
        successes = sum(1 for episode in episodes if episode.get("success"))
        failures = total - successes
        return {
            "total_episodes": total,
            "successful": successes,
            "failed": failures,
            "success_rate": successes / total if total else 0.0,
            "backend": "json-local",
        }


class ArtHippoNet:
    """Complete memory system combining episodic, semantic, and procedural stores."""

    def __init__(self, agent_id: str, prefer_local_fallback: bool = False) -> None:
        self.agent_id = agent_id
        self.episodic, self.semantic = self._build_memory_backends(prefer_local_fallback=prefer_local_fallback)
        self.procedural = ProceduralMemory()
        logger.info("arthipponet_initialized", extra={"agent_id": agent_id})

    def _build_memory_backends(self, prefer_local_fallback: bool = False) -> tuple[Any, Any]:
        if not prefer_local_fallback:
            try:
                return EpisodicMemory(), SemanticMemory()
            except ModuleNotFoundError as exc:
                logger.warning(
                    "vector_memory_unavailable_using_local_fallback",
                    extra={"reason": str(exc), "agent_id": self.agent_id},
                )
        return LocalEpisodicMemory(), LocalSemanticMemory()

    def integrated_recall(self, situation: str) -> Dict[str, Any]:
        logger.info("integrated_recall_start", extra={"agent_id": self.agent_id, "situation": situation[:50]})

        episodes = self.episodic.retrieve_similar(
            query=situation,
            agent_id=self.agent_id,
            n_results=3,
        )
        facts = self.semantic.query_facts(situation, n_results=5)
        concepts = self.semantic.query_concepts(situation, n_results=3)
        procedures = self.procedural.retrieve_by_description(situation, n_results=3)

        context = {
            "situation": situation,
            "past_experiences": [
                {"task": episode.task, "outcome": episode.outcome, "success": episode.success}
                for episode in episodes
            ],
            "relevant_facts": [f"{fact.subject} {fact.predicate} {fact.object}" for fact in facts],
            "relevant_concepts": [{"name": concept.name, "definition": concept.definition} for concept in concepts],
            "applicable_procedures": [
                {"name": procedure.name, "description": procedure.description, "steps": len(procedure.steps)}
                for procedure in procedures
            ],
        }

        logger.info(
            "integrated_recall_complete",
            extra={
                "agent_id": self.agent_id,
                "episodes": len(episodes),
                "facts": len(facts),
                "concepts": len(concepts),
                "procedures": len(procedures),
            },
        )
        return context

    def learn_from_success(self, episode: Episode) -> None:
        self.episodic.store_episode(episode)

        if episode.success and len(episode.actions) >= 2:
            procedure_name = f"procedure_from_{episode.id[:8]}" if episode.id else f"procedure_{int(time.time())}"
            self.procedural.extract_procedure_from_episode(
                episode_data={"actions": episode.actions, "tags": episode.tags or []},
                name=procedure_name,
                description=f"Learned from: {episode.task}",
            )

        logger.info("learned_from_episode", extra={"episode_id": episode.id, "agent_id": self.agent_id})

    def get_complete_stats(self) -> Dict[str, Any]:
        return {
            "episodic": self.episodic.get_statistics(self.agent_id),
            "semantic": self.semantic.get_statistics(),
            "procedural": self.procedural.get_statistics(),
        }


class CompleteAgentMemoryInterface:
    """High-level agent interface for ArtHippoNet."""

    def __init__(self, agent_id: str, prefer_local_fallback: bool = False) -> None:
        self.agent_id = agent_id
        self.memory = ArtHippoNet(agent_id, prefer_local_fallback=prefer_local_fallback)

    def remember_task(
        self,
        task: str,
        actions: List[str],
        outcome: str,
        success: bool = True,
        observations: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        episode = Episode(
            id=None,
            agent_id=self.agent_id,
            timestamp=time.time(),
            task=task,
            actions=actions,
            observations=observations or [],
            outcome=outcome,
            success=success,
            reward=1.0 if success else 0.0,
            tags=tags or [],
        )
        episode_id = self.memory.episodic.store_episode(episode)
        if success:
            self.memory.learn_from_success(episode)
        return episode_id

    def recall_for_situation(self, situation: str) -> Dict[str, Any]:
        return self.memory.integrated_recall(situation)

    def learn_fact(self, subject: str, predicate: str, obj: str) -> str:
        fact = Fact(id=None, subject=subject, predicate=predicate, object=obj)
        return self.memory.semantic.store_fact(fact)

    def define_concept(self, name: str, definition: str, category: str, examples: Optional[List[str]] = None) -> str:
        concept = Concept(id=None, name=name, definition=definition, category=category, examples=examples or [])
        return self.memory.semantic.store_concept(concept)

    def get_procedure(self, name: str) -> Optional[Procedure]:
        return self.memory.procedural.retrieve_by_name(name)


AgentMemoryInterface = CompleteAgentMemoryInterface

__all__ = [
    "ArtHippoNet",
    "AgentMemoryInterface",
    "CompleteAgentMemoryInterface",
    "LocalEpisodicMemory",
    "LocalSemanticMemory",
]
