"""Socratic questioning logic for guided learning."""

import json
from typing import Optional
from anthropic import Anthropic


class SocraticEngine:
    """Generates Socratic questions and hints to guide learning."""

    def __init__(self, client: Anthropic):
        self.client = client

    def generate_guiding_question(
        self,
        topic: str,
        topic_content: dict,
        learner_context: str,
        previous_exchanges: list[dict],
    ) -> str:
        """Generate a Socratic question to guide the learner."""
        guiding_questions = topic_content.get("guiding_questions", [])
        key_concepts = topic_content.get("key_concepts", [])

        recent_context = ""
        if previous_exchanges:
            recent_context = "\n".join(
                f"{ex['role'].title()}: {ex['content']}"
                for ex in previous_exchanges[-3:]
            )

        prompt = f"""You are a Socratic tutor teaching {topic}.

Key concepts to guide toward:
{json.dumps(key_concepts, indent=2)}

Sample guiding questions (use as inspiration):
{json.dumps(guiding_questions, indent=2)}

Learner context: {learner_context}

Recent conversation:
{recent_context}

Generate ONE thought-provoking question that:
1. Connects to what the learner already knows or just said
2. Guides them toward discovering a key concept
3. Is appropriate for their level
4. Encourages thinking rather than just recall

Respond with ONLY the question, nothing else."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()

    def generate_hint(
        self,
        problem: dict,
        learner_answer: str,
        hints_given: int = 0,
    ) -> str:
        """Generate a hint for a practice problem without giving the answer."""
        hints = problem.get("hints", [])

        # If we have predefined hints, use them in order
        if hints_given < len(hints):
            return hints[hints_given]

        # Otherwise, generate a custom hint
        prompt = f"""The student is working on this genetics problem:
{problem.get('question', '')}

Their answer was: {learner_answer}
Correct answer: {problem.get('answer', '')}

They've already received {hints_given} hints.

Generate a helpful hint that:
1. Doesn't give away the answer directly
2. Points them in the right direction
3. Addresses any apparent misconception in their answer
4. Uses simple language

Respond with ONLY the hint, nothing else."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=150,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()

    def generate_analogy(
        self,
        concept: str,
        learner_level: str,
    ) -> str:
        """Generate a relatable analogy for an abstract concept."""
        prompt = f"""Create a simple, relatable analogy to explain this genetics concept to a {learner_level} level student:

Concept: {concept}

Requirements:
1. Use everyday objects or experiences
2. Make it memorable and accurate
3. Keep it brief (1-2 sentences)
4. Avoid technical jargon

Respond with ONLY the analogy, nothing else."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()

    def evaluate_understanding(
        self,
        topic: str,
        learner_response: str,
        expected_concepts: list[str],
    ) -> dict:
        """Evaluate if the learner's response shows understanding."""
        prompt = f"""Evaluate this genetics student's response for understanding of {topic}.

Student said: "{learner_response}"

Expected concepts they should demonstrate understanding of:
{json.dumps(expected_concepts, indent=2)}

Respond with a JSON object:
{{
    "understanding_level": "none" | "partial" | "good" | "excellent",
    "concepts_demonstrated": ["list of concepts they showed understanding of"],
    "concepts_missing": ["list of concepts they didn't demonstrate"],
    "suggested_follow_up": "a follow-up question or next step"
}}

Respond with ONLY the JSON, nothing else."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            return json.loads(response.content[0].text.strip())
        except json.JSONDecodeError:
            return {
                "understanding_level": "partial",
                "concepts_demonstrated": [],
                "concepts_missing": expected_concepts,
                "suggested_follow_up": "Can you tell me more about what you understand?",
            }

    def determine_response_type(
        self,
        learner_response: str,
        current_topic: str,
        teaching_state: str,
    ) -> str:
        """Determine what type of response is appropriate."""
        prompt = f"""A genetics student is learning about {current_topic}.
Current teaching state: {teaching_state}

Student's message: "{learner_response}"

What type of tutor response is most appropriate?
- "guide": Ask a guiding question to deepen understanding
- "explain": Provide a brief explanation (they seem confused)
- "encourage": Affirm their understanding and move forward
- "clarify": They asked a question that needs answering
- "redirect": They're off-topic, gently bring them back
- "hint": They're working on a problem and need a hint

Respond with ONLY one of these words."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=20,
            messages=[{"role": "user", "content": prompt}],
        )

        response_type = response.content[0].text.strip().lower()
        valid_types = ["guide", "explain", "encourage", "clarify", "redirect", "hint"]

        return response_type if response_type in valid_types else "guide"
