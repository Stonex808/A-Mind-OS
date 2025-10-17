"""Integrated ArtHippoNet memory system."""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from refocus_core.logging import setup_logging

from .episodic import Episode, EpisodicMemory
from .procedural import ProceduralMemory, Procedure
from .semantic import Concept, Fact, SemanticMemory

logger = setup_logging("memory-integration")


class ArtHippoNet:
    """Complete memory system combining episodic, semantic, and procedural stores."""

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        self.episodic = EpisodicMemory()
        self.semantic = SemanticMemory()
        self.procedural = ProceduralMemory()
        logger.info("arthipponet_initialized", extra={"agent_id": agent_id})

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

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        self.memory = ArtHippoNet(agent_id)

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
]
