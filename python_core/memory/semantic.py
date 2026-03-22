"""Semantic memory system storing facts and concepts."""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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

from ..refocus_core.logging import setup_logging

logger = setup_logging("semantic-memory")


@dataclass
class Fact:
    """A single piece of knowledge."""

    id: Optional[str]
    subject: str
    predicate: str
    object: str
    confidence: float = 1.0
    source: Optional[str] = None
    timestamp: float = 0.0


@dataclass
class Concept:
    """A concept definition with metadata."""

    id: Optional[str]
    name: str
    definition: str
    category: str
    related_concepts: Optional[List[str]] = field(default_factory=list)
    examples: Optional[List[str]] = field(default_factory=list)


class SemanticMemory:
    """Semantic memory combining vector search with a simple knowledge graph."""

    def __init__(self, persist_directory: str = "./data/memory/semantic") -> None:
        if chromadb is None or Settings is None:  # pragma: no cover
            raise ModuleNotFoundError(
                "chromadb is required for SemanticMemory. Install it to enable local vector storage."
            ) from _CHROMADB_ERROR

        if SentenceTransformer is None:  # pragma: no cover
            raise ModuleNotFoundError(
                "sentence-transformers is required for SemanticMemory embeddings."
            ) from _SENTENCE_TRANSFORMER_ERROR

        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.Client(
            Settings(
                persist_directory=str(self.persist_dir / "chroma"),
                anonymized_telemetry=False,
            )
        )
        self.facts_collection = self.client.get_or_create_collection(
            name="facts",
            metadata={"description": "Factual knowledge"},
        )
        self.concepts_collection = self.client.get_or_create_collection(
            name="concepts",
            metadata={"description": "Concept definitions"},
        )

        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.knowledge_graph: Dict[str, List[Tuple[str, str]]] = {}
        self._load_knowledge_graph()

        logger.info("semantic_memory_initialized", persist_directory=str(self.persist_dir))

    def store_fact(self, fact: Fact) -> str:
        if not fact.id:
            fact.id = str(uuid.uuid4())

        fact_text = f"{fact.subject} {fact.predicate} {fact.object}"
        embedding = self.encoder.encode(fact_text).tolist()
        metadata = {
            "subject": fact.subject,
            "predicate": fact.predicate,
            "object": fact.object,
            "confidence": fact.confidence,
            "source": fact.source or "unknown",
        }

        self.facts_collection.add(
            ids=[fact.id],
            embeddings=[embedding],
            documents=[fact_text],
            metadatas=[metadata],
        )

        self.knowledge_graph.setdefault(fact.subject, []).append((fact.predicate, fact.object))
        self._save_knowledge_graph()

        logger.debug("fact_stored", extra={"fact_id": fact.id, "subject": fact.subject})
        return fact.id

    def store_concept(self, concept: Concept) -> str:
        if not concept.id:
            concept.id = str(uuid.uuid4())

        concept_text = f"{concept.name}: {concept.definition}"
        if concept.examples:
            concept_text += f" Examples: {', '.join(concept.examples)}"

        embedding = self.encoder.encode(concept_text).tolist()
        metadata = {
            "name": concept.name,
            "category": concept.category,
        }

        self.concepts_collection.add(
            ids=[concept.id],
            embeddings=[embedding],
            documents=[concept_text],
            metadatas=[metadata],
        )

        self._save_concept(concept)
        logger.debug("concept_stored", extra={"concept_id": concept.id, "name": concept.name})
        return concept.id

    def query_facts(self, query: str, n_results: int = 5, min_confidence: float = 0.0) -> List[Fact]:
        embedding = self.encoder.encode(query).tolist()
        results = self.facts_collection.query(query_embeddings=[embedding], n_results=n_results)

        matches: List[Fact] = []
        for idx, fact_id in enumerate(results.get("ids", [[]])[0]):
            metadata = results.get("metadatas", [[]])[0][idx]
            if metadata["confidence"] < min_confidence:
                continue
            matches.append(
                Fact(
                    id=fact_id,
                    subject=metadata["subject"],
                    predicate=metadata["predicate"],
                    object=metadata["object"],
                    confidence=metadata["confidence"],
                    source=metadata.get("source"),
                )
            )

        logger.info(
            "semantic_query",
            extra={"query": query[:50], "facts": len(matches), "min_confidence": min_confidence},
        )
        return matches

    def query_concepts(self, query: str, n_results: int = 3) -> List[Concept]:
        embedding = self.encoder.encode(query).tolist()
        results = self.concepts_collection.query(query_embeddings=[embedding], n_results=n_results)

        concepts: List[Concept] = []
        for concept_id in results.get("ids", [[]])[0]:
            concept = self._load_concept(concept_id)
            if concept:
                concepts.append(concept)

        logger.info("concept_query", extra={"query": query[:50], "concepts": len(concepts)})
        return concepts

    def get_related_facts(self, subject: str, max_depth: int = 2) -> List[Fact]:
        related: List[Fact] = []
        visited = set()
        queue: List[Tuple[str, int]] = [(subject, 0)]

        while queue:
            current, depth = queue.pop(0)
            if current in visited or depth > max_depth:
                continue
            visited.add(current)

            for predicate, obj in self.knowledge_graph.get(current, []):
                related.append(
                    Fact(
                        id=str(uuid.uuid4()),
                        subject=current,
                        predicate=predicate,
                        object=obj,
                    )
                )
                queue.append((obj, depth + 1))

        logger.debug("related_facts", extra={"subject": subject, "count": len(related)})
        return related

    def learn_from_text(self, text: str, source: str = "learned") -> None:
        sentences = [sentence.strip() for sentence in text.split(".") if sentence.strip()]
        for sentence in sentences:
            if " is " not in sentence:
                continue
            subject, remainder = sentence.split(" is ", 1)
            fact = Fact(
                id=None,
                subject=subject.strip(),
                predicate="is",
                object=remainder.strip(),
                confidence=0.8,
                source=source,
            )
            self.store_fact(fact)

        logger.info("learned_from_text", extra={"source": source, "sentences": len(sentences)})

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "total_facts": self.facts_collection.count(),
            "total_concepts": self.concepts_collection.count(),
            "knowledge_graph_entities": len(self.knowledge_graph),
        }

    def _save_knowledge_graph(self) -> None:
        path = self.persist_dir / "knowledge_graph.json"
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(self.knowledge_graph, handle, indent=2)

    def _load_knowledge_graph(self) -> None:
        path = self.persist_dir / "knowledge_graph.json"
        if not path.exists():
            return
        with open(path, "r", encoding="utf-8") as handle:
            self.knowledge_graph = json.load(handle)
        logger.debug("knowledge_graph_loaded", extra={"entities": len(self.knowledge_graph)})

    def _save_concept(self, concept: Concept) -> None:
        concepts_dir = self.persist_dir / "concepts"
        concepts_dir.mkdir(parents=True, exist_ok=True)
        with open(concepts_dir / f"{concept.id}.json", "w", encoding="utf-8") as handle:
            json.dump(
                {
                    "id": concept.id,
                    "name": concept.name,
                    "definition": concept.definition,
                    "category": concept.category,
                    "related_concepts": concept.related_concepts or [],
                    "examples": concept.examples or [],
                },
                handle,
                indent=2,
            )

    def _load_concept(self, concept_id: str) -> Optional[Concept]:
        path = self.persist_dir / "concepts" / f"{concept_id}.json"
        if not path.exists():
            return None
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return Concept(**data)


def seed_programming_knowledge(memory: SemanticMemory) -> None:
    """Seed semantic memory with baseline programming concepts and facts."""

    concepts = [
        Concept(
            id=None,
            name="Variable",
            definition="A named storage location that holds a value",
            category="programming",
            examples=["x = 5", "name = 'Alice'"],
        ),
        Concept(
            id=None,
            name="Function",
            definition="A reusable block of code that performs a specific task",
            category="programming",
            examples=["def add(a, b): return a + b"],
        ),
        Concept(
            id=None,
            name="Loop",
            definition="A control structure that repeats a block of code",
            category="programming",
            examples=["for i in range(10):", "while condition:"],
        ),
        Concept(
            id=None,
            name="Recursion",
            definition="When a function calls itself to solve a problem",
            category="programming",
            examples=["factorial(n) calls factorial(n-1)"],
        ),
    ]
    for concept in concepts:
        memory.store_concept(concept)

    facts = [
        Fact(None, "Python", "is_a", "programming language"),
        Fact(None, "Python", "uses", "indentation for blocks"),
        Fact(None, "Python", "supports", "object-oriented programming"),
        Fact(None, "JavaScript", "is_a", "programming language"),
        Fact(None, "JavaScript", "runs_in", "web browsers"),
        Fact(None, "Rust", "is_a", "systems programming language"),
        Fact(None, "Rust", "provides", "memory safety"),
        Fact(None, "Variable", "stores", "data"),
        Fact(None, "Function", "accepts", "parameters"),
        Fact(None, "Loop", "enables", "iteration"),
    ]
    for fact in facts:
        memory.store_fact(fact)

    logger.info("programming_knowledge_seeded")


__all__ = ["SemanticMemory", "Fact", "Concept", "seed_programming_knowledge"]
