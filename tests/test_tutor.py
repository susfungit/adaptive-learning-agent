"""Tests for the main tutor agent (without API calls)."""

import tempfile
import shutil
import pytest

from content.topics import (
    TOPIC_HIERARCHY,
    get_topic,
    get_prerequisites,
    get_next_topic,
    get_topics_for_level,
)


class TestTopics:
    """Tests for topic management."""

    def test_topic_hierarchy_exists(self):
        """Test that topic hierarchy is defined."""
        assert len(TOPIC_HIERARCHY) >= 3

    def test_get_topic(self):
        """Test getting a topic by ID."""
        topic = get_topic("punnett_squares")
        assert topic is not None
        assert topic["name"] == "Punnett Squares"

    def test_get_prerequisites(self):
        """Test getting prerequisites for a topic."""
        prereqs = get_prerequisites("punnett_squares")
        assert "mendelian_inheritance" in prereqs

    def test_get_next_topic_with_mastered(self):
        """Test getting next topic based on mastery."""
        mastered = ["dna_basics", "mendelian_inheritance"]
        next_topic = get_next_topic("mendelian_inheritance", mastered)
        assert next_topic == "punnett_squares"

    def test_get_topics_for_level(self):
        """Test getting topics for a specific level."""
        beginner_topics = get_topics_for_level("beginner")
        assert "dna_basics" in beginner_topics
        assert "punnett_squares" in beginner_topics


class TestTutorBasics:
    """Basic tests for tutor functionality (no API)."""

    def test_content_loading(self):
        """Test that content files can be loaded."""
        import json
        from pathlib import Path

        content_path = Path(__file__).parent.parent / "content" / "genetics_content.json"
        assert content_path.exists()

        with open(content_path) as f:
            content = json.load(f)

        assert "punnett_squares" in content
        assert "explanation" in content["punnett_squares"]

    def test_problems_loading(self):
        """Test that problems file can be loaded."""
        import json
        from pathlib import Path

        problems_path = Path(__file__).parent.parent / "content" / "problems.json"
        assert problems_path.exists()

        with open(problems_path) as f:
            problems = json.load(f)

        assert "punnett_squares" in problems
        assert len(problems["punnett_squares"]) >= 3

    def test_problem_structure(self):
        """Test that problems have required fields."""
        import json
        from pathlib import Path

        problems_path = Path(__file__).parent.parent / "content" / "problems.json"
        with open(problems_path) as f:
            problems = json.load(f)

        for problem in problems["punnett_squares"]:
            assert "id" in problem
            assert "question" in problem
            assert "answer" in problem
            assert "hints" in problem


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
