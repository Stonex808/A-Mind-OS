"""Episodic memory system for ArtHippoNet."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:  # pragma: no cover - optional dependency
    import chromadb
    from chromadb.config import Settings
except ModuleNotFoundError as exc:  # pragma: no cover - import guard
    chromadb = None  # type: ignore[assignment]
    Settings = None  # type: ignore[assignment]
    _CHROMADB_ERROR = exc
else:  # pragma: no cover - import guard
    _CHROMADB_ERROR = None

try:  # pragma: no cover - optional dependency
    from sentence_transformers import SentenceTransformer
except ModuleNotFoundError as exc:  # pragma: no cover - import guard
    SentenceTransformer = None  # type: ignore[assignment]
    _SENTENCE_TRANSFORMER_ERROR = exc
else:  # pragma: no cover - import guard
    _SENTENCE_TRANSFORMER_ERROR = None

from refocus_core.logging import setup_logging

logger = setup_logging("episodic-memory")


@dataclass
class Episode:
    """A single episodic memory."""

    id: Optional[str]
    agent_id: str
    timestamp: float
    task: str
    actions: List[str]
    observations: List[str]
    outcome: str
    location: Optional[str] = None
    other_agents: Optional[List[str]] = None
    success: bool = True
    reward: float = 0.0
    tags: Optional[List[str]] = None


class EpisodicMemory:
    """Persistent episodic memory backed by ChromaDB."""

    def __init__(self, persist_directory: str = "./data/memory/episodic") -> None:
        if chromadb is None or Settings is None:  # pragma: no cover - runtime guard
            raise ModuleNotFoundError(
                "chromadb is required for EpisodicMemory. Install it locally to keep data offline."
            ) from _CHROMADB_ERROR

        if SentenceTransformer is None:  # pragma: no cover - runtime guard
            raise ModuleNotFoundError(
                "sentence-transformers is required for EpisodicMemory embeddings."
            ) from _SENTENCE_TRANSFORMER_ERROR

        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.Client(
            Settings(
                persist_directory=str(self.persist_dir / "chroma"),
                anonymized_telemetry=False,
            )
        )
        self.collection = self.client.get_or_create_collection(
            name="episodes",
            metadata={"description": "Agent episodic memories"},
        )

        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.episodes_store = self.persist_dir / "episodes"
        self.episodes_store.mkdir(parents=True, exist_ok=True)

        logger.info("episodic_memory_initialized", persist_directory=str(self.persist_dir))

    def store_episode(self, episode: Episode) -> str:
        """Persist an episode and its embedding."""

        if not episode.id:
            episode.id = str(uuid.uuid4())

        document = self._create_searchable_text(episode)
        embedding = self.encoder.encode(document).tolist()

        metadata = {
            "agent_id": episode.agent_id,
            "timestamp": episode.timestamp,
            "success": episode.success,
            "reward": episode.reward,
            "tags": ",".join(episode.tags) if episode.tags else "",
        }

        self.collection.add(
            ids=[episode.id],
            embeddings=[embedding],
            documents=[document],
            metadatas=[metadata],
        )

        self._store_full_episode(episode)

        logger.debug(
            "episode_stored",
            extra={
                "episode_id": episode.id,
                "agent_id": episode.agent_id,
                "success": episode.success,
                "timestamp": episode.timestamp,
            },
        )

        return episode.id

    def retrieve_similar(
        self,
        query: str,
        agent_id: str,
        n_results: int = 3,
        success_only: bool = False,
    ) -> List[Episode]:
        """Return episodes similar to the query."""

        embedding = self.encoder.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=n_results * 2,
        )

        found: List[Episode] = []
        for idx, episode_id in enumerate(results.get("ids", [[]])[0]):
            metadata = results.get("metadatas", [[]])[0][idx]
            if metadata.get("agent_id") != agent_id:
                continue
            if success_only and not metadata.get("success", False):
                continue

            episode = self._load_full_episode(episode_id)
            if episode:
                found.append(episode)
            if len(found) >= n_results:
                break

        logger.debug(
            "episodes_retrieved",
            extra={"query": query[:50], "count": len(found), "agent_id": agent_id},
        )
        return found

    def get_statistics(self, agent_id: Optional[str] = None) -> Dict[str, Any]:
        """Return aggregate statistics for stored memories."""

        total = self.collection.count()
        if agent_id is None:
            return {"total_episodes": total}

        successes = 0
        failures = 0
        for path in self.episodes_store.glob("*.json"):
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if data.get("agent_id") != agent_id:
                continue
            if data.get("success", False):
                successes += 1
            else:
                failures += 1

        return {
            "total_episodes": successes + failures,
            "successful": successes,
            "failed": failures,
            "success_rate": successes / (successes + failures) if successes + failures else 0.0,
        }

    def _create_searchable_text(self, episode: Episode) -> str:
        parts: List[str] = [
            f"Task: {episode.task}",
            f"Outcome: {episode.outcome}",
            f"Actions: {'; '.join(episode.actions)}",
        ]
        if episode.observations:
            parts.append(f"Observations: {'; '.join(episode.observations)}")
        if episode.tags:
            parts.append(f"Tags: {', '.join(episode.tags)}")
        timestamp = datetime.fromtimestamp(episode.timestamp).isoformat()
        parts.append(f"Timestamp: {timestamp}")
        return " | ".join(parts)

    def _store_full_episode(self, episode: Episode) -> None:
        path = self.episodes_store / f"{episode.id}.json"
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(asdict(episode), handle, indent=2)

    def _load_full_episode(self, episode_id: str) -> Optional[Episode]:
        path = self.episodes_store / f"{episode_id}.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        data["other_agents"] = data.get("other_agents") or None
        data["tags"] = data.get("tags") or None
        return Episode(**data)


__all__ = ["Episode", "EpisodicMemory"]
