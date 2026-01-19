"""Learner profile management."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
from .storage import Storage


@dataclass
class KnowledgeState:
    """Tracks what the learner knows."""

    topics_mastered: dict[str, int] = field(default_factory=dict)  # topic_id -> mastery score (0-100)
    topics_in_progress: list[str] = field(default_factory=list)
    misconceptions: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "KnowledgeState":
        return cls(**data)


@dataclass
class ProgressHistory:
    """Tracks the learner's learning journey."""

    assessment_results: list[dict] = field(default_factory=list)
    quiz_scores: list[dict] = field(default_factory=list)
    session_summaries: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ProgressHistory":
        return cls(**data)


@dataclass
class LearnerProfile:
    """Complete learner profile with all state."""

    learner_id: str
    name: str
    current_level: str = "beginner"  # beginner | intermediate | advanced
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    total_sessions: int = 0
    knowledge: KnowledgeState = field(default_factory=KnowledgeState)
    progress: ProgressHistory = field(default_factory=ProgressHistory)
    last_topic: Optional[str] = None
    last_session_summary: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "learner_id": self.learner_id,
            "name": self.name,
            "current_level": self.current_level,
            "created_at": self.created_at,
            "total_sessions": self.total_sessions,
            "knowledge": self.knowledge.to_dict(),
            "progress": self.progress.to_dict(),
            "last_topic": self.last_topic,
            "last_session_summary": self.last_session_summary,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LearnerProfile":
        return cls(
            learner_id=data["learner_id"],
            name=data["name"],
            current_level=data.get("current_level", "beginner"),
            created_at=data.get("created_at", datetime.now().isoformat()),
            total_sessions=data.get("total_sessions", 0),
            knowledge=KnowledgeState.from_dict(data.get("knowledge", {})),
            progress=ProgressHistory.from_dict(data.get("progress", {})),
            last_topic=data.get("last_topic"),
            last_session_summary=data.get("last_session_summary"),
        )

    def update_mastery(self, topic_id: str, score: int) -> None:
        """Update mastery score for a topic."""
        self.knowledge.topics_mastered[topic_id] = min(100, max(0, score))
        if score >= 70 and topic_id in self.knowledge.topics_in_progress:
            self.knowledge.topics_in_progress.remove(topic_id)

    def add_misconception(self, misconception: str) -> None:
        """Record a misconception to address later."""
        if misconception not in self.knowledge.misconceptions:
            self.knowledge.misconceptions.append(misconception)

    def add_session_summary(self, summary: dict) -> None:
        """Add a session summary to progress history."""
        self.progress.session_summaries.append(summary)
        self.last_session_summary = summary.get("summary", "")

    def add_quiz_score(self, quiz_result: dict) -> None:
        """Add a quiz score to progress history."""
        self.progress.quiz_scores.append(quiz_result)


class LearnerManager:
    """Manages learner profiles with persistence."""

    def __init__(self, storage: Storage):
        self.storage = storage

    def create_learner(self, learner_id: str, name: str) -> LearnerProfile:
        """Create a new learner profile."""
        profile = LearnerProfile(learner_id=learner_id, name=name)
        self.storage.save_learner(learner_id, profile.to_dict())
        return profile

    def get_learner(self, learner_id: str) -> Optional[LearnerProfile]:
        """Get an existing learner profile."""
        data = self.storage.load_learner(learner_id)
        if data is None:
            return None
        return LearnerProfile.from_dict(data)

    def save_learner(self, profile: LearnerProfile) -> None:
        """Save a learner profile."""
        self.storage.save_learner(profile.learner_id, profile.to_dict())

    def learner_exists(self, learner_id: str) -> bool:
        """Check if a learner exists."""
        return self.storage.learner_exists(learner_id)
