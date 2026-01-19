"""Tests for assessment module."""

import pytest

from assessment.questions import (
    DIAGNOSTIC_QUESTIONS,
    get_question,
    get_first_question,
    get_next_question,
)
from assessment.evaluator import AnswerEvaluator
from assessment.diagnostic import DiagnosticAssessment


class TestQuestions:
    """Tests for the question bank."""

    def test_diagnostic_questions_exist(self):
        """Test that diagnostic questions are defined."""
        assert len(DIAGNOSTIC_QUESTIONS) >= 5

    def test_get_question(self):
        """Test getting a question by ID."""
        q = get_question("diag_001")
        assert q is not None
        assert q["id"] == "diag_001"

    def test_get_first_question(self):
        """Test getting the first question."""
        q = get_first_question()
        assert q is not None
        assert "question" in q

    def test_get_next_question_correct(self):
        """Test getting next question after correct answer."""
        next_q = get_next_question("diag_001", was_correct=True)
        assert next_q is not None
        assert next_q["id"] == "diag_002"

    def test_get_next_question_wrong(self):
        """Test getting next question after wrong answer."""
        next_q = get_next_question("diag_001", was_correct=False)
        assert next_q is not None
        assert next_q["id"] == "diag_001b"


class TestAnswerEvaluator:
    """Tests for the answer evaluator."""

    def test_evaluate_simple_exact_match(self):
        """Test exact match evaluation."""
        evaluator = AnswerEvaluator()
        result = evaluator.evaluate_simple("DNA", "DNA", ["dna"])
        assert result["correct"] == True

    def test_evaluate_simple_case_insensitive(self):
        """Test case insensitive matching."""
        evaluator = AnswerEvaluator()
        result = evaluator.evaluate_simple("dna", "DNA", ["dna"])
        assert result["correct"] == True

    def test_evaluate_simple_acceptable_answer(self):
        """Test acceptable answer matching."""
        evaluator = AnswerEvaluator()
        result = evaluator.evaluate_simple("25 percent", "25%", ["25%", "25", "1/4"])
        assert result["correct"] == True

    def test_evaluate_pattern_good(self):
        """Test pattern matching with good understanding."""
        evaluator = AnswerEvaluator()
        result = evaluator.evaluate_pattern(
            "DNA contains instructions for building proteins and determines traits",
            ["instruction", "code", "information", "genes", "traits"]
        )
        assert result["correct"] == True

    def test_evaluate_pattern_partial(self):
        """Test pattern matching with partial understanding."""
        evaluator = AnswerEvaluator()
        result = evaluator.evaluate_pattern(
            "DNA is in cells",
            ["instruction", "code", "information", "genes", "traits"]
        )
        assert result["correct"] == False


class TestDiagnosticAssessment:
    """Tests for the diagnostic assessment."""

    def test_start_assessment(self):
        """Test starting an assessment."""
        assessment = DiagnosticAssessment()
        first_q = assessment.start()

        assert first_q is not None
        assert "question" in first_q
        assert assessment.current_question is not None

    def test_submit_correct_answer(self):
        """Test submitting a correct answer."""
        assessment = DiagnosticAssessment()
        assessment.start()

        result = assessment.submit_answer("DNA")

        assert result["evaluation"]["correct"] == True
        assert len(assessment.results) == 1

    def test_get_level_beginner(self):
        """Test level determination for beginner."""
        assessment = DiagnosticAssessment()
        assessment.results = [
            {"correct": True, "level": "beginner"},
            {"correct": False, "level": "intermediate"},
            {"correct": False, "level": "advanced"},
        ]

        level = assessment.get_level()
        assert level == "beginner"

    def test_get_knowledge_gaps(self):
        """Test identifying knowledge gaps."""
        assessment = DiagnosticAssessment()
        assessment.results = [
            {"correct": True, "topic": "dna_basics"},
            {"correct": False, "partial": False, "topic": "punnett_squares"},
        ]

        gaps = assessment.get_knowledge_gaps()
        assert "punnett_squares" in gaps
        assert "dna_basics" not in gaps


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
