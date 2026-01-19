"""Answer evaluation logic using Claude API."""

import json
import re
from typing import Optional
from anthropic import Anthropic


class AnswerEvaluator:
    """Evaluates learner answers using a combination of pattern matching and Claude."""

    def __init__(self, client: Optional[Anthropic] = None):
        self.client = client

    def evaluate_simple(self, answer: str, expected: str, acceptable: list[str]) -> dict:
        """Simple evaluation using string matching."""
        answer_lower = answer.lower().strip()

        # Check exact match or acceptable answers
        is_correct = (
            answer_lower == expected.lower()
            or any(acc.lower() in answer_lower for acc in acceptable)
        )

        return {
            "correct": is_correct,
            "partial": False,
            "feedback": None,
        }

    def evaluate_pattern(self, answer: str, patterns: list[str]) -> dict:
        """Evaluate open-ended answers using pattern matching."""
        answer_lower = answer.lower()

        matches = sum(1 for p in patterns if p.lower() in answer_lower)
        total = len(patterns)

        if matches >= 2:
            return {"correct": True, "partial": False, "understanding": "good"}
        elif matches >= 1:
            return {"correct": False, "partial": True, "understanding": "partial"}
        else:
            return {"correct": False, "partial": False, "understanding": "minimal"}

    def evaluate_with_llm(
        self, question: str, answer: str, expected: str, topic: str
    ) -> dict:
        """Use Claude to evaluate more complex answers."""
        if self.client is None:
            # Fallback to simple evaluation
            return {"correct": False, "partial": False, "feedback": "Unable to evaluate"}

        prompt = f"""You are evaluating a student's answer in a genetics tutoring session.

Question: {question}
Expected answer: {expected}
Student's answer: {answer}
Topic: {topic}

Evaluate the student's answer and respond with a JSON object containing:
- "correct": boolean (true if the answer demonstrates correct understanding)
- "partial": boolean (true if the answer shows some understanding but is incomplete)
- "feedback": string (brief, encouraging feedback for the student)
- "misconception": string or null (any misconception you detect in the answer)

Be generous - if the student shows understanding of the concept even if wording differs, mark it correct.
Respond ONLY with the JSON object, no other text."""

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )

            result_text = response.content[0].text.strip()
            # Try to extract JSON from the response
            json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            return {"correct": False, "partial": False, "feedback": "Unable to parse evaluation"}

        except Exception as e:
            return {"correct": False, "partial": False, "feedback": f"Evaluation error: {str(e)}"}

    def evaluate(
        self,
        question: dict,
        answer: str,
        use_llm: bool = True,
    ) -> dict:
        """Main evaluation method that chooses the appropriate strategy."""
        if question.get("answer") == "open_ended":
            # Use pattern matching for open-ended questions
            patterns = question.get("acceptable_patterns", [])
            result = self.evaluate_pattern(answer, patterns)
            # For open-ended, we're more lenient
            result["correct"] = result["correct"] or result["partial"]
            return result

        # Try simple evaluation first
        expected = question.get("answer", "")
        acceptable = question.get("acceptable_answers", [])
        simple_result = self.evaluate_simple(answer, expected, acceptable)

        if simple_result["correct"]:
            return simple_result

        # If not clearly correct and LLM is available, use it for nuanced evaluation
        if use_llm and self.client is not None:
            return self.evaluate_with_llm(
                question=question.get("question", ""),
                answer=answer,
                expected=expected,
                topic=question.get("topic", "genetics"),
            )

        return simple_result
