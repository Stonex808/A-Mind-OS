"""Test script for the complete ArtHippoNet system."""

from __future__ import annotations

import time

from python_core.memory import ArtHippoNet, Episode


def test_arthipponet() -> None:
    print("=== Testing Complete ArtHippoNet System ===\n")

    memory = ArtHippoNet("test_agent")

    print("1. Storing episodic memory...")
    episode = Episode(
        id=None,
        agent_id="test_agent",
        timestamp=time.time(),
        task="Build a web scraper for news articles",
        actions=[
            "Imported requests and BeautifulSoup",
            "Made HTTP request to news site",
            "Parsed HTML content",
            "Extracted article titles and links",
            "Saved to JSON file",
        ],
        observations=[
            "Site uses JavaScript rendering",
            "Need to handle rate limiting",
        ],
        outcome="Successfully scraped 50 articles",
        success=True,
        tags=["web", "scraping", "data"],
    )
    memory.episodic.store_episode(episode)
    memory.learn_from_success(episode)

    print("2. Storing semantic knowledge...")
    memory.semantic.learn_from_text(
        "Web scraping is the process of extracting data from websites. "
        "BeautifulSoup is a Python library for parsing HTML. "
        "HTTP requests are used to fetch web pages.",
        source="learning",
    )

    print("\n3. Testing integrated recall...\n")
    situation = "I need to extract data from a website"
    context = memory.integrated_recall(situation)

    print(f"Integrated recall for: '{situation}'\n")
    print("Past Experiences:")
    for exp in context["past_experiences"]:
        print(f"  - {exp['task']}")
        print(f"    Outcome: {exp['outcome']}")
        print(f"    Success: {exp['success']}\n")

    print("Relevant Facts:")
    for fact in context["relevant_facts"]:
        print(f"  - {fact}")

    print("\nRelevant Concepts:")
    for concept in context["relevant_concepts"]:
        print(f"  - {concept['name']}: {concept['definition']}")

    print("\nApplicable Procedures:")
    for proc in context["applicable_procedures"]:
        print(f"  - {proc['name']}: {proc['description']}")
        print(f"    Steps: {proc['steps']}")

    print("\n4. Memory Statistics:")
    stats = memory.get_complete_stats()

    print("\nEpisodic Memory:")
    for key, value in stats["episodic"].items():
        print(f"  {key}: {value}")

    print("\nSemantic Memory:")
    for key, value in stats["semantic"].items():
        print(f"  {key}: {value}")

    print("\nProcedural Memory:")
    for key, value in stats["procedural"].items():
        print(f"  {key}: {value}")

    print("\n=== Test Complete ===")


if __name__ == "__main__":
    test_arthipponet()
