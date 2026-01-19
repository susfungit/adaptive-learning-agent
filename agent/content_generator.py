"""Dynamic content generation for any topic using Claude."""

import json
import re
from typing import Optional
from anthropic import Anthropic


class ContentGenerator:
    """Generates tutoring content dynamically for any subject."""

    def __init__(self, client: Anthropic):
        self.client = client
        self.cache = {}  # Cache generated content

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text that might have markdown code blocks."""
        # Remove markdown code blocks if present
        text = text.strip()

        # Try to find JSON in code blocks
        code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if code_block_match:
            text = code_block_match.group(1).strip()

        # Find JSON array or object
        if text.startswith('['):
            match = re.search(r'\[[\s\S]*\]', text)
            if match:
                return match.group()
        elif text.startswith('{'):
            match = re.search(r'\{[\s\S]*\}', text)
            if match:
                return match.group()

        return text

    def generate_topic_overview(self, subject: str, learner_level: str = "beginner") -> dict:
        """Generate a topic hierarchy and overview for any subject."""
        cache_key = f"overview_{subject}_{learner_level}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = f"""You are an expert educator. Create a learning overview for the subject: "{subject}"

The learner is at a {learner_level} level.

Respond with a JSON object containing:
{{
    "subject": "{subject}",
    "description": "Brief description of what this subject covers",
    "learning_objectives": ["3-5 key things the learner will understand"],
    "subtopics": [
        {{
            "id": "subtopic_1",
            "name": "First subtopic name",
            "description": "What this subtopic covers",
            "order": 1
        }},
        // 3-5 subtopics in logical learning order
    ],
    "prerequisites": ["Any assumed knowledge"],
    "real_world_applications": ["2-3 practical applications"]
}}

Keep it appropriate for a {learner_level} learner. Respond ONLY with valid JSON."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            json_text = self._extract_json(response.content[0].text)
            result = json.loads(json_text)
            self.cache[cache_key] = result
            return result
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Failed to parse topic overview: {e}")
            return {
                "subject": subject,
                "description": f"Learning about {subject}",
                "learning_objectives": [f"Understand the basics of {subject}"],
                "subtopics": [
                    {"id": "basics", "name": "Fundamentals", "description": f"Core concepts of {subject}", "order": 1},
                    {"id": "intermediate", "name": "Key Concepts", "description": f"Important ideas in {subject}", "order": 2},
                    {"id": "practice", "name": "Application", "description": f"Applying {subject} knowledge", "order": 3},
                ],
                "prerequisites": [],
                "real_world_applications": [],
            }

    def generate_assessment_questions(self, subject: str, num_questions: int = 5) -> list[dict]:
        """Generate diagnostic questions for any subject."""
        cache_key = f"assessment_{subject}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = f"""Create {num_questions} diagnostic assessment questions for the subject: "{subject}"

These questions should span from beginner to advanced to help determine a student's current knowledge level.

Respond with a JSON array of questions:
[
    {{
        "id": "q1",
        "level": "beginner",
        "question": "The question text",
        "answer": "The expected answer (keep it short)",
        "acceptable_answers": ["list", "of", "acceptable", "variations"],
        "concept": "What concept this tests"
    }},
    // More questions from beginner to advanced
]

Mix question types:
- 2 beginner questions (basic recall/understanding)
- 2 intermediate questions (application)
- 1 advanced question (analysis/synthesis)

Respond ONLY with valid JSON array."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            json_text = self._extract_json(response.content[0].text)
            result = json.loads(json_text)
            self.cache[cache_key] = result
            return result
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Failed to parse assessment questions: {e}")
            # Return a set of generic but useful assessment questions
            return [
                {
                    "id": "q1",
                    "level": "beginner",
                    "question": f"What do you already know about {subject}?",
                    "answer": "open_ended",
                    "acceptable_answers": [],
                    "concept": "prior_knowledge",
                },
                {
                    "id": "q2",
                    "level": "beginner",
                    "question": f"Why are you interested in learning {subject}?",
                    "answer": "open_ended",
                    "acceptable_answers": [],
                    "concept": "motivation",
                },
                {
                    "id": "q3",
                    "level": "intermediate",
                    "question": f"Can you describe any key concepts or terms related to {subject}?",
                    "answer": "open_ended",
                    "acceptable_answers": [],
                    "concept": "terminology",
                },
                {
                    "id": "q4",
                    "level": "intermediate",
                    "question": f"Have you tried applying {subject} in any practical way?",
                    "answer": "open_ended",
                    "acceptable_answers": [],
                    "concept": "application",
                },
                {
                    "id": "q5",
                    "level": "advanced",
                    "question": f"What challenges or questions do you have about {subject}?",
                    "answer": "open_ended",
                    "acceptable_answers": [],
                    "concept": "depth",
                },
            ]

    def generate_lesson_content(self, subject: str, subtopic: str, learner_level: str) -> dict:
        """Generate teaching content for a specific subtopic."""
        cache_key = f"lesson_{subject}_{subtopic}_{learner_level}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = f"""Create teaching content for:
Subject: {subject}
Subtopic: {subtopic}
Learner Level: {learner_level}

Respond with a JSON object:
{{
    "explanation": "Clear explanation appropriate for {learner_level} level (2-3 paragraphs)",
    "key_concepts": ["3-5 main concepts to understand"],
    "analogies": ["2-3 relatable analogies to explain difficult concepts"],
    "examples": ["2-3 concrete examples"],
    "common_mistakes": ["2-3 common misconceptions or errors"],
    "guiding_questions": ["3-4 Socratic questions to guide discovery"],
    "check_understanding": ["2-3 questions to verify comprehension"]
}}

Make the content engaging and appropriate for the learner's level.
Respond ONLY with valid JSON."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            json_text = self._extract_json(response.content[0].text)
            result = json.loads(json_text)
            self.cache[cache_key] = result
            return result
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Failed to parse lesson content: {e}")
            return {
                "explanation": f"Let's explore {subtopic} in {subject}.",
                "key_concepts": [subtopic],
                "analogies": [],
                "examples": [],
                "common_mistakes": [],
                "guiding_questions": [
                    f"What do you think {subtopic} means?",
                    f"Why might {subtopic} be important in {subject}?",
                    f"Can you think of an example of {subtopic}?",
                ],
                "check_understanding": [],
            }

    def generate_practice_problems(self, subject: str, subtopic: str, difficulty: str, count: int = 3) -> list[dict]:
        """Generate practice problems for a subtopic."""
        cache_key = f"problems_{subject}_{subtopic}_{difficulty}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        prompt = f"""Create {count} practice problems for:
Subject: {subject}
Subtopic: {subtopic}
Difficulty: {difficulty}

Respond with a JSON array of problems:
[
    {{
        "id": "p1",
        "question": "The problem statement",
        "answer": "The correct answer",
        "acceptable_answers": ["variations", "of", "correct", "answer"],
        "hints": [
            "First hint (gentle nudge)",
            "Second hint (more specific)",
            "Third hint (almost gives it away)"
        ],
        "explanation": "Full explanation of the solution",
        "concept": "What concept this tests"
    }}
]

Make problems practical and engaging. Include step-by-step hints that guide without giving away the answer.
Respond ONLY with valid JSON array."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            json_text = self._extract_json(response.content[0].text)
            result = json.loads(json_text)
            self.cache[cache_key] = result
            return result
        except (json.JSONDecodeError, Exception) as e:
            print(f"Warning: Failed to parse practice problems: {e}")
            return [
                {
                    "id": "p1",
                    "question": f"Explain a key concept from {subtopic} in your own words.",
                    "answer": "open_ended",
                    "acceptable_answers": [],
                    "hints": [
                        "Think about the main ideas we discussed.",
                        "Try to use an example to illustrate.",
                        "What would you tell a friend about this?",
                    ],
                    "explanation": f"This helps reinforce your understanding of {subtopic}.",
                    "concept": subtopic,
                },
                {
                    "id": "p2",
                    "question": f"Give a real-world example of how {subtopic} applies in practice.",
                    "answer": "open_ended",
                    "acceptable_answers": [],
                    "hints": [
                        "Think about everyday situations.",
                        "Consider professional applications.",
                        "What problems does this help solve?",
                    ],
                    "explanation": f"Connecting {subtopic} to real life deepens understanding.",
                    "concept": subtopic,
                },
            ]

    def generate_socratic_response(
        self,
        subject: str,
        subtopic: str,
        learner_message: str,
        conversation_context: str,
        learner_level: str,
    ) -> str:
        """Generate a Socratic tutoring response."""
        prompt = f"""You are a Socratic tutor teaching {subject}, specifically {subtopic}.
The learner is at a {learner_level} level.

Recent conversation:
{conversation_context}

Learner just said: "{learner_message}"

Respond as a Socratic tutor:
- If they show understanding, ask a deeper question or move forward
- If they're confused, ask a simpler question or give a hint
- If they're stuck, provide a small piece of information then ask again
- Use analogies and examples relevant to their message
- Keep responses concise (2-4 sentences)
- Ask ONE question at a time
- Be encouraging but not patronizing

Respond directly as the tutor (no JSON, just your teaching response)."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()

    def evaluate_answer(self, question: str, expected: str, learner_answer: str, subject: str) -> dict:
        """Evaluate a learner's answer using Claude."""
        prompt = f"""Evaluate this student's answer:

Subject: {subject}
Question: {question}
Expected Answer: {expected}
Student's Answer: {learner_answer}

Respond with a JSON object:
{{
    "correct": true/false,
    "partial": true/false (shows some understanding but incomplete),
    "feedback": "Brief encouraging feedback",
    "misconception": "Any misconception detected, or null"
}}

Be generous - if they show understanding even with different wording, mark correct.
Respond ONLY with valid JSON."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )

        try:
            json_text = self._extract_json(response.content[0].text)
            return json.loads(json_text)
        except (json.JSONDecodeError, Exception):
            # Fallback to simple matching or generous acceptance for open-ended
            if expected.lower() == "open_ended":
                # For open-ended questions, accept any thoughtful response
                has_content = len(learner_answer.strip()) > 10
                return {
                    "correct": has_content,
                    "partial": not has_content,
                    "feedback": "Thanks for sharing!" if has_content else "Could you tell me a bit more?",
                    "misconception": None,
                }
            answer_lower = learner_answer.lower().strip()
            expected_lower = expected.lower().strip()
            is_correct = answer_lower == expected_lower or expected_lower in answer_lower
            return {
                "correct": is_correct,
                "partial": False,
                "feedback": "Let's continue." if is_correct else "Let me help you with that.",
                "misconception": None,
            }

    def generate_alternative_explanation(
        self, question: str, subject: str, attempt_number: int
    ) -> str:
        """Generate an alternative explanation when learner is struggling."""
        prompt = f"""A student is struggling with this question about {subject}:

Question: {question}

They've tried {attempt_number} times and still haven't gotten it right. 

Provide a brief alternative explanation (2-3 sentences) that:
1. Approaches the concept from a different angle
2. Uses a simple analogy or example
3. Breaks down the concept into smaller parts
4. Is encouraging and supportive

Respond with ONLY the explanation, nothing else."""

        response = self.client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text.strip()

    def clear_cache(self):
        """Clear the content cache."""
        self.cache = {}
