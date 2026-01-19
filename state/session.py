"""Session state management for current tutoring session."""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class SessionState:
    """Tracks the current tutoring session."""

    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    learner_id: str = ""
    current_topic: Optional[str] = None
    current_subtopic: Optional[str] = None
    conversation_history: list[dict] = field(default_factory=list)
    questions_asked: int = 0
    problems_attempted: list[dict] = field(default_factory=list)
    session_start: str = field(default_factory=lambda: datetime.now().isoformat())
    flow_state: str = "start"  # start | assessment | teaching | practice | review
    assessment_answers: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "SessionState":
        return cls(**data)

    def add_exchange(self, role: str, content: str) -> None:
        """Add a conversation exchange to history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })
        # Keep only last 20 exchanges to manage context size
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-20:]

    def add_problem_attempt(self, problem_id: str, answer: str, correct: bool, feedback: str) -> None:
        """Record a practice problem attempt."""
        self.problems_attempted.append({
            "problem_id": problem_id,
            "answer": answer,
            "correct": correct,
            "feedback": feedback,
            "timestamp": datetime.now().isoformat()
        })

    def add_assessment_answer(self, question_id: str, answer: str, correct: bool) -> None:
        """Record an assessment answer."""
        self.assessment_answers.append({
            "question_id": question_id,
            "answer": answer,
            "correct": correct,
            "timestamp": datetime.now().isoformat()
        })

    def get_session_summary(self) -> dict:
        """Generate a summary of the session."""
        correct_problems = sum(1 for p in self.problems_attempted if p["correct"])
        total_problems = len(self.problems_attempted)

        return {
            "session_id": self.session_id,
            "topic_covered": self.current_topic,
            "questions_asked": self.questions_asked,
            "problems_attempted": total_problems,
            "problems_correct": correct_problems,
            "accuracy": correct_problems / total_problems if total_problems > 0 else None,
            "duration_start": self.session_start,
            "timestamp": datetime.now().isoformat()
        }

    def get_recent_context(self, n: int = 5) -> list[dict]:
        """Get the most recent conversation exchanges for context."""
        return self.conversation_history[-n:]


class Session:
    """Manages a tutoring session."""

    def __init__(self, learner_id: str):
        self.state = SessionState(learner_id=learner_id)

    def start_assessment(self) -> None:
        """Transition to assessment flow."""
        self.state.flow_state = "assessment"

    def start_teaching(self, topic: str) -> None:
        """Transition to teaching flow."""
        self.state.flow_state = "teaching"
        self.state.current_topic = topic

    def start_practice(self) -> None:
        """Transition to practice flow."""
        self.state.flow_state = "practice"

    def start_review(self) -> None:
        """Transition to review flow."""
        self.state.flow_state = "review"

    def record_exchange(self, role: str, content: str) -> None:
        """Record a conversation exchange."""
        self.state.add_exchange(role, content)
        if role == "assistant":
            self.state.questions_asked += 1

    def record_problem(self, problem_id: str, answer: str, correct: bool, feedback: str) -> None:
        """Record a practice problem attempt."""
        self.state.add_problem_attempt(problem_id, answer, correct, feedback)

    def get_summary(self) -> dict:
        """Get session summary."""
        return self.state.get_session_summary()
