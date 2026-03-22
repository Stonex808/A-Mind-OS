from __future__ import annotations

from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from python_core.memory.episodic import Episode, EpisodicMemory
from python_core.memory.memory_integration import ArtHippoNet, CompleteAgentMemoryInterface
from python_core.memory.procedural import ActionStep, ProceduralMemory, Procedure
from python_core.memory.semantic import Concept, Fact, SemanticMemory


class FakeEmbedding(list):
    def tolist(self) -> list[float]:
        return list(self)


class FakeEncoder:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name

    def encode(self, text: str) -> FakeEmbedding:
        normalized = text.lower()
        return FakeEmbedding([
            float(len(normalized)),
            float(sum(ord(ch) for ch in normalized) % 997),
            float(len(set(normalized.split()))),
        ])


class FakeCollection:
    def __init__(self) -> None:
        self.records: list[dict] = []

    def add(self, ids, embeddings, documents, metadatas) -> None:
        for record_id, embedding, document, metadata in zip(ids, embeddings, documents, metadatas):
            self.records.append(
                {
                    "id": record_id,
                    "embedding": list(embedding),
                    "document": document,
                    "metadata": metadata,
                }
            )

    def query(self, query_embeddings, n_results):
        query = query_embeddings[0]
        ranked = sorted(
            self.records,
            key=lambda record: (
                sum(abs(a - b) for a, b in zip(record["embedding"], query)),
                record["id"],
            ),
        )[:n_results]
        return {
            "ids": [[record["id"] for record in ranked]],
            "metadatas": [[record["metadata"] for record in ranked]],
            "documents": [[record["document"] for record in ranked]],
        }

    def count(self) -> int:
        return len(self.records)


class FakeClient:
    def __init__(self, settings) -> None:
        self.settings = settings
        self.collections: dict[str, FakeCollection] = {}

    def get_or_create_collection(self, name: str, metadata=None):
        return self.collections.setdefault(name, FakeCollection())


class FakeSettings:
    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs


@pytest.fixture(autouse=True)
def fake_vector_dependencies(monkeypatch):
    from python_core.memory import episodic, semantic

    fake_chromadb = type("FakeChromaModule", (), {"Client": FakeClient})
    monkeypatch.setattr(episodic, "chromadb", fake_chromadb)
    monkeypatch.setattr(episodic, "Settings", FakeSettings)
    monkeypatch.setattr(episodic, "SentenceTransformer", FakeEncoder)
    monkeypatch.setattr(semantic, "chromadb", fake_chromadb)
    monkeypatch.setattr(semantic, "Settings", FakeSettings)
    monkeypatch.setattr(semantic, "SentenceTransformer", FakeEncoder)


def test_episodic_memory_round_trip_uses_local_temp_directory(tmp_path: Path) -> None:
    memory = EpisodicMemory(persist_directory=str(tmp_path / "episodic"))
    episode = Episode(
        id=None,
        agent_id="agent-1",
        timestamp=1_700_000_000.0,
        task="Sort a list of numbers",
        actions=["open editor", "write sorting function"],
        observations=["input is small"],
        outcome="Sorted list correctly",
        success=True,
        reward=1.0,
        tags=["sorting", "python"],
    )

    episode_id = memory.store_episode(episode)
    recalled = memory.retrieve_similar("sort numbers", agent_id="agent-1", n_results=1)
    payload_path = tmp_path / "episodic" / "episodes" / f"{episode_id}.json"

    assert payload_path.exists()
    assert [item.id for item in recalled] == [episode_id]
    assert recalled[0].task == "Sort a list of numbers"
    assert memory.get_statistics("agent-1") == {
        "total_episodes": 1,
        "successful": 1,
        "failed": 0,
        "success_rate": 1.0,
    }


def test_semantic_memory_persists_facts_and_concepts_locally(tmp_path: Path) -> None:
    memory = SemanticMemory(persist_directory=str(tmp_path / "semantic"))

    fact_id = memory.store_fact(Fact(id=None, subject="Python", predicate="is", object="interpreted", confidence=0.9))
    concept_id = memory.store_concept(
        Concept(id=None, name="Function", definition="Reusable block of code", category="programming", examples=["def add(): ..."])
    )

    facts = memory.query_facts("interpreted language", n_results=1)
    concepts = memory.query_concepts("reusable code block", n_results=1)

    assert facts[0].id == fact_id
    assert facts[0].subject == "Python"
    assert concepts[0].id == concept_id
    assert (tmp_path / "semantic" / "knowledge_graph.json").exists()
    assert (tmp_path / "semantic" / "concepts" / f"{concept_id}.json").exists()
    assert memory.get_statistics() == {
        "total_facts": 1,
        "total_concepts": 1,
        "knowledge_graph_entities": 1,
    }


def test_procedural_memory_round_trip_and_stats(tmp_path: Path) -> None:
    memory = ProceduralMemory(persist_directory=str(tmp_path / "procedural"))
    procedure = Procedure(
        id=None,
        name="local_backup",
        description="Create a local encrypted backup archive",
        steps=[ActionStep(action="tar", parameters={"path": "./data/memory"}, expected_outcome="archive created")],
        tags=["backup", "security"],
    )

    procedure_id = memory.store_procedure(procedure)
    memory.record_execution(procedure_id, success=True, execution_time=2.5)
    reloaded = ProceduralMemory(persist_directory=str(tmp_path / "procedural"))

    assert reloaded.retrieve_by_name("local_backup") is not None
    assert reloaded.retrieve_by_tags(["security"])[0].id == procedure_id
    assert reloaded.get_statistics() == {
        "total_procedures": 1,
        "total_executions": 1,
        "total_successes": 1,
        "overall_success_rate": 1.0,
    }


def test_remember_task_does_not_store_duplicate_episode_records(tmp_path: Path) -> None:
    memory = ArtHippoNet("agent-2")
    memory.episodic = EpisodicMemory(persist_directory=str(tmp_path / "episodic"))
    memory.semantic = SemanticMemory(persist_directory=str(tmp_path / "semantic"))
    memory.procedural = ProceduralMemory(persist_directory=str(tmp_path / "procedural"))

    interface = CompleteAgentMemoryInterface("agent-2")
    interface.memory = memory

    episode_id = interface.remember_task(
        task="Write dependency docs",
        actions=["inspect README", "update setup section"],
        outcome="Documentation clarified",
        success=True,
        observations=["offline setup needed"],
        tags=["docs"],
    )

    stored_payloads = list((tmp_path / "episodic" / "episodes").glob("*.json"))

    assert [path.stem for path in stored_payloads] == [episode_id]
    assert memory.episodic.get_statistics("agent-2")["total_episodes"] == 1
    assert memory.procedural.get_statistics()["total_procedures"] == 1


def test_learn_from_success_can_store_unsaved_episode_once(tmp_path: Path) -> None:
    memory = ArtHippoNet("agent-3")
    memory.episodic = EpisodicMemory(persist_directory=str(tmp_path / "episodic"))
    memory.semantic = SemanticMemory(persist_directory=str(tmp_path / "semantic"))
    memory.procedural = ProceduralMemory(persist_directory=str(tmp_path / "procedural"))

    episode = Episode(
        id=None,
        agent_id="agent-3",
        timestamp=1_700_000_123.0,
        task="Recover local backup",
        actions=["mount encrypted drive", "restore archive"],
        observations=["backup verified"],
        outcome="Recovered successfully",
        success=True,
        reward=1.0,
        tags=["backup"],
    )

    memory.learn_from_success(episode)
    memory.learn_from_success(episode)

    stored_payloads = list((tmp_path / "episodic" / "episodes").glob("*.json"))
    assert len(stored_payloads) == 1
    assert memory.episodic.get_statistics("agent-3")["total_episodes"] == 1
    assert memory.procedural.get_statistics()["total_procedures"] == 2
