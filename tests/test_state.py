"""Tests for state management."""

import tempfile
import shutil
import pytest
from pathlib import Path

from state.storage import Storage
from state.learner import LearnerProfile, LearnerManager, KnowledgeState
from state.session import Session


class TestStorage:
    """Tests for the Storage class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.storage = Storage(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        shutil.rmtree(self.temp_dir)

    def test_save_and_load_learner(self):
        """Test saving and loading learner data."""
        data = {"learner_id": "test1", "name": "Test User", "level": "beginner"}
        self.storage.save_learner("test1", data)

        loaded = self.storage.load_learner("test1")
        assert loaded["learner_id"] == "test1"
        assert loaded["name"] == "Test User"

    def test_learner_exists(self):
        """Test checking if learner exists."""
        assert not self.storage.learner_exists("nonexistent")

        self.storage.save_learner("exists", {"name": "Exists"})
        assert self.storage.learner_exists("exists")

    def test_list_learners(self):
        """Test listing all learners."""
        self.storage.save_learner("user1", {"name": "User 1"})
        self.storage.save_learner("user2", {"name": "User 2"})

        learners = self.storage.list_learners()
        assert "user1" in learners
        assert "user2" in learners


class TestLearnerProfile:
    """Tests for LearnerProfile."""

    def test_create_profile(self):
        """Test creating a learner profile."""
        profile = LearnerProfile(learner_id="test", name="Test User")

        assert profile.learner_id == "test"
        assert profile.name == "Test User"
        assert profile.current_level == "beginner"
        assert profile.total_sessions == 0

    def test_update_mastery(self):
        """Test updating topic mastery."""
        profile = LearnerProfile(learner_id="test", name="Test")
        profile.knowledge.topics_in_progress = ["punnett_squares"]

        profile.update_mastery("punnett_squares", 80)

        assert profile.knowledge.topics_mastered["punnett_squares"] == 80
        assert "punnett_squares" not in profile.knowledge.topics_in_progress

    def test_to_dict_and_from_dict(self):
        """Test serialization round trip."""
        original = LearnerProfile(learner_id="test", name="Test User")
        original.current_level = "intermediate"
        original.update_mastery("dna_basics", 90)

        data = original.to_dict()
        restored = LearnerProfile.from_dict(data)

        assert restored.learner_id == original.learner_id
        assert restored.current_level == original.current_level
        assert restored.knowledge.topics_mastered == original.knowledge.topics_mastered


class TestSession:
    """Tests for Session."""

    def test_create_session(self):
        """Test creating a session."""
        session = Session("test_learner")

        assert session.state.learner_id == "test_learner"
        assert session.state.flow_state == "start"

    def test_record_exchange(self):
        """Test recording conversation exchanges."""
        session = Session("test")

        session.record_exchange("user", "Hello")
        session.record_exchange("assistant", "Hi there!")

        assert len(session.state.conversation_history) == 2
        assert session.state.questions_asked == 1

    def test_record_problem(self):
        """Test recording problem attempts."""
        session = Session("test")
        session.start_practice()

        session.record_problem("ps_001", "25%", True, "Correct!")

        assert len(session.state.problems_attempted) == 1
        assert session.state.problems_attempted[0]["correct"] == True

    def test_session_summary(self):
        """Test getting session summary."""
        session = Session("test")
        session.state.current_topic = "punnett_squares"
        session.record_problem("ps_001", "25%", True, "Correct!")
        session.record_problem("ps_002", "50%", False, "Incorrect")

        summary = session.get_summary()

        assert summary["problems_attempted"] == 2
        assert summary["problems_correct"] == 1
        assert summary["accuracy"] == 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
