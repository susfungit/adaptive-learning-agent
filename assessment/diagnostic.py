"""Initial level assessment for new learners."""

from typing import Optional
from anthropic import Anthropic

from .questions import get_first_question, get_next_question, get_question
from .evaluator import AnswerEvaluator


class DiagnosticAssessment:
    """Conducts diagnostic assessment to determine learner's level."""

    def __init__(self, client: Optional[Anthropic] = None):
        self.evaluator = AnswerEvaluator(client)
        self.results = []
        self.current_question = None

    def start(self) -> dict:
        """Start the diagnostic assessment and return the first question."""
        self.results = []
        self.current_question = get_first_question()
        return self.current_question

    def submit_answer(self, answer: str) -> dict:
        """Submit an answer and get evaluation + next question."""
        if self.current_question is None:
            return {"error": "No active question", "complete": True}

        # Evaluate the answer
        evaluation = self.evaluator.evaluate(self.current_question, answer)

        # Record the result
        self.results.append({
            "question_id": self.current_question["id"],
            "question": self.current_question["question"],
            "answer": answer,
            "correct": evaluation.get("correct", False),
            "partial": evaluation.get("partial", False),
            "level": self.current_question.get("level", "beginner"),
            "topic": self.current_question.get("topic", ""),
        })

        # Get next question
        is_correct = evaluation.get("correct", False)
        next_q = get_next_question(self.current_question["id"], is_correct)

        self.current_question = next_q

        return {
            "evaluation": evaluation,
            "next_question": next_q,
            "complete": next_q is None,
        }

    def get_level(self) -> str:
        """Determine the learner's level based on assessment results."""
        if not self.results:
            return "beginner"

        # Count correct answers by level
        level_scores = {"beginner": 0, "intermediate": 0, "advanced": 0}
        level_counts = {"beginner": 0, "intermediate": 0, "advanced": 0}

        for result in self.results:
            level = result.get("level", "beginner")
            level_counts[level] += 1
            if result.get("correct"):
                level_scores[level] += 1

        # Calculate percentages
        beginner_pct = level_scores["beginner"] / max(level_counts["beginner"], 1)
        intermediate_pct = level_scores["intermediate"] / max(level_counts["intermediate"], 1)
        advanced_pct = level_scores["advanced"] / max(level_counts["advanced"], 1)

        # Determine level
        if advanced_pct >= 0.5 and intermediate_pct >= 0.5:
            return "advanced"
        elif intermediate_pct >= 0.5 and beginner_pct >= 0.5:
            return "intermediate"
        else:
            return "beginner"

    def get_knowledge_gaps(self) -> list[str]:
        """Identify topics where the learner struggled."""
        gaps = []
        for result in self.results:
            if not result.get("correct") and not result.get("partial"):
                topic = result.get("topic")
                if topic and topic not in gaps:
                    gaps.append(topic)
        return gaps

    def get_strengths(self) -> list[str]:
        """Identify topics where the learner excelled."""
        strengths = []
        for result in self.results:
            if result.get("correct"):
                topic = result.get("topic")
                if topic and topic not in strengths:
                    strengths.append(topic)
        return strengths

    def get_summary(self) -> dict:
        """Get a complete summary of the assessment."""
        correct_count = sum(1 for r in self.results if r.get("correct"))
        total = len(self.results)

        return {
            "level": self.get_level(),
            "questions_answered": total,
            "correct_answers": correct_count,
            "accuracy": correct_count / total if total > 0 else 0,
            "knowledge_gaps": self.get_knowledge_gaps(),
            "strengths": self.get_strengths(),
            "results": self.results,
        }

    def get_recommended_start_topic(self) -> str:
        """Recommend a starting topic based on assessment."""
        level = self.get_level()
        gaps = self.get_knowledge_gaps()

        # If they struggled with basics, start there
        if "dna_basics" in gaps:
            return "dna_basics"
        if "mendelian_inheritance" in gaps:
            return "mendelian_inheritance"
        if "punnett_squares" in gaps:
            return "punnett_squares"

        # Otherwise, recommend based on level
        if level == "beginner":
            return "mendelian_inheritance"  # Skip DNA basics if they know it
        elif level == "intermediate":
            return "punnett_squares"
        else:
            return "pedigree_analysis"
