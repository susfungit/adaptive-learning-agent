"""Main tutoring agent logic - Dynamic version that works with any topic."""

from typing import Optional
from anthropic import Anthropic

from .content_generator import ContentGenerator
from .prompts import SYSTEM_PROMPT
from state.learner import LearnerProfile, LearnerManager
from state.session import Session
from state.storage import Storage


class DynamicTutor:
    """Dynamic tutoring agent that can teach any subject."""

    def __init__(self, data_dir: str = "data/learners"):
        self.client = Anthropic()
        self.storage = Storage(data_dir)
        self.learner_manager = LearnerManager(self.storage)
        self.content_gen = ContentGenerator(self.client)

        # Session state
        self.profile: Optional[LearnerProfile] = None
        self.session: Optional[Session] = None

        # Dynamic content state
        self.subject: Optional[str] = None
        self.topic_overview: Optional[dict] = None
        self.current_subtopic: Optional[dict] = None
        self.current_subtopic_index: int = 0
        self.lesson_content: Optional[dict] = None
        self.assessment_questions: list[dict] = []
        self.current_question_index: int = 0
        self.practice_problems: list[dict] = []
        self.current_problem: Optional[dict] = None
        self.current_problem_index: int = 0
        self.hints_given: int = 0

    def start_session(self, learner_id: str, name: Optional[str] = None) -> str:
        """Start a tutoring session for a learner."""
        if self.learner_manager.learner_exists(learner_id):
            self.profile = self.learner_manager.get_learner(learner_id)
            self.profile.total_sessions += 1
            self.session = Session(learner_id)

            # Check if they have a previous subject
            if self.profile.last_topic:
                self.session.state.flow_state = "returning"
                return self._welcome_back()

        if name is None:
            name = learner_id

        if not self.profile:
            self.profile = self.learner_manager.create_learner(learner_id, name)

        self.session = Session(learner_id)
        self.session.state.flow_state = "topic_selection"
        return self._welcome_new()

    def _welcome_new(self) -> str:
        """Welcome message for new learners."""
        name = self.profile.name if self.profile else "there"
        return f"""Hi {name}! I'm your personal learning guide.

I can help you learn about ANY topic through questions and exploration. I use the Socratic method - which means I'll guide you to discover answers yourself rather than just telling you.

**What would you like to learn about today?**

You can say things like:
- "I want to learn Python programming"
- "Teach me about photosynthesis"
- "Help me understand World War 2"
- "I'd like to learn calculus"

What subject interests you?"""

    def _welcome_back(self) -> str:
        """Welcome message for returning learners."""
        name = self.profile.name
        last_subject = self.profile.last_topic
        level = self.profile.current_level

        return f"""Welcome back, {name}!

Last time you were learning about **{last_subject}** (at {level} level).

What would you like to do?
1. **Continue** with {last_subject}
2. **Start fresh** with a new topic

Just type 'continue' or tell me what new topic you'd like to explore!"""

    def handle_input(self, user_input: str) -> str:
        """Handle user input and return tutor response."""
        if not self.session:
            return "Please start a session first."

        self.session.record_exchange("user", user_input)

        flow = self.session.state.flow_state
        response = ""

        if flow == "topic_selection":
            response = self._handle_topic_selection(user_input)
        elif flow == "returning":
            response = self._handle_returning_choice(user_input)
        elif flow == "assessment":
            response = self._handle_assessment(user_input)
        elif flow == "teaching":
            response = self._handle_teaching(user_input)
        elif flow == "practice":
            response = self._handle_practice(user_input)
        else:
            response = self._handle_topic_selection(user_input)

        self.session.record_exchange("assistant", response)
        return response

    def _handle_topic_selection(self, user_input: str) -> str:
        """Handle topic selection from user."""
        self.subject = user_input.strip()
        self.profile.last_topic = self.subject
        self.learner_manager.save_learner(self.profile)

        # Generate topic overview
        self.topic_overview = self.content_gen.generate_topic_overview(
            self.subject, self.profile.current_level
        )

        # Generate assessment questions
        self.assessment_questions = self.content_gen.generate_assessment_questions(
            self.subject, num_questions=5
        )

        subtopics = self.topic_overview.get("subtopics", [])
        subtopic_list = "\n".join(
            f"  {i+1}. {st.get('name', 'Topic')}" for i, st in enumerate(subtopics)
        )

        self.session.state.flow_state = "assessment"
        self.session.state.current_topic = self.subject
        self.current_question_index = 0

        return f"""Great choice! Let's explore **{self.subject}**.

{self.topic_overview.get('description', '')}

Here's what we'll cover:
{subtopic_list}

First, let me ask you a few questions to understand what you already know. This helps me tailor the lessons to your level.

Ready? Here's the first question:

**{self.assessment_questions[0].get('question', 'What do you already know about this topic?')}**"""

    def _handle_returning_choice(self, user_input: str) -> str:
        """Handle returning learner's choice."""
        lower = user_input.lower().strip()

        if "continue" in lower or "1" == lower:
            self.subject = self.profile.last_topic
            self.topic_overview = self.content_gen.generate_topic_overview(
                self.subject, self.profile.current_level
            )
            return self._start_teaching()
        else:
            # They want a new topic
            self.session.state.flow_state = "topic_selection"
            return self._handle_topic_selection(user_input)

    def _handle_assessment(self, user_input: str) -> str:
        """Handle assessment question answers."""
        # Check if assessment is already done and user is ready to start
        if self.current_question_index >= len(self.assessment_questions):
            lower = user_input.lower().strip()
            if lower in ["yes", "ready", "ok", "sure", "let's go", "start", "begin"]:
                return self._start_teaching()
            else:
                # Answer any questions they have
                return self.content_gen.generate_socratic_response(
                    subject=self.subject,
                    subtopic="getting started",
                    learner_message=user_input,
                    conversation_context="",
                    learner_level=self.profile.current_level,
                )

        current_q = self.assessment_questions[self.current_question_index]

        # Evaluate the answer
        evaluation = self.content_gen.evaluate_answer(
            question=current_q.get("question", ""),
            expected=current_q.get("answer", ""),
            learner_answer=user_input,
            subject=self.subject,
        )

        # Record result
        self.session.state.add_assessment_answer(
            current_q.get("id", f"q{self.current_question_index}"),
            user_input,
            evaluation.get("correct", False),
        )

        # Move to next question
        self.current_question_index += 1

        # Feedback
        if evaluation.get("correct"):
            feedback = "Nice! "
        elif evaluation.get("partial"):
            feedback = "You're on the right track. "
        else:
            feedback = "That's okay - this helps me understand where you're at. "

        # Check if assessment is complete
        if self.current_question_index >= len(self.assessment_questions):
            return feedback + "\n\n" + self._complete_assessment()

        # Next question
        next_q = self.assessment_questions[self.current_question_index]
        return f"""{feedback}

Next question:

**{next_q.get('question', '')}**"""

    def _complete_assessment(self) -> str:
        """Complete assessment and determine level."""
        # Count correct answers by level
        results = self.session.state.assessment_answers
        correct_by_level = {"beginner": 0, "intermediate": 0, "advanced": 0}
        total_by_level = {"beginner": 0, "intermediate": 0, "advanced": 0}

        for i, result in enumerate(results):
            if i < len(self.assessment_questions):
                level = self.assessment_questions[i].get("level", "beginner")
                total_by_level[level] += 1
                if result.get("correct"):
                    correct_by_level[level] += 1

        # Determine level
        if correct_by_level["advanced"] > 0 and correct_by_level["intermediate"] > 0:
            level = "advanced"
        elif correct_by_level["intermediate"] > 0 and correct_by_level["beginner"] > 0:
            level = "intermediate"
        else:
            level = "beginner"

        self.profile.current_level = level
        self.learner_manager.save_learner(self.profile)

        # Regenerate content at appropriate level
        self.topic_overview = self.content_gen.generate_topic_overview(
            self.subject, level
        )

        level_messages = {
            "beginner": "Let's start from the foundations and build up your understanding step by step.",
            "intermediate": "You have some background here! Let's deepen your understanding.",
            "advanced": "Impressive! You already know quite a bit. Let's explore some advanced concepts.",
        }

        return f"""Assessment complete! Based on your answers, you're at a **{level}** level.

{level_messages[level]}

Ready to begin? Just say **'yes'** or ask any questions you have!"""

    def _start_teaching(self) -> str:
        """Start teaching the first subtopic."""
        self.session.state.flow_state = "teaching"

        subtopics = self.topic_overview.get("subtopics", [])
        if not subtopics:
            subtopics = [{"id": "main", "name": self.subject, "description": f"Core concepts of {self.subject}"}]

        self.current_subtopic_index = 0
        self.current_subtopic = subtopics[0]

        # Generate lesson content
        self.lesson_content = self.content_gen.generate_lesson_content(
            self.subject,
            self.current_subtopic.get("name", self.subject),
            self.profile.current_level,
        )

        # Start with a guiding question
        guiding_questions = self.lesson_content.get("guiding_questions", [])
        first_question = guiding_questions[0] if guiding_questions else f"What do you think {self.current_subtopic.get('name', 'this')} means?"

        return f"""Let's start with **{self.current_subtopic.get('name', self.subject)}**.

{first_question}"""

    def _handle_teaching(self, user_input: str) -> str:
        """Handle teaching dialogue using Socratic method."""
        lower = user_input.lower().strip()

        # Check for special commands
        if any(word in lower for word in ["practice", "problem", "quiz", "test me"]):
            return self._start_practice()

        if any(word in lower for word in ["next", "move on", "next topic"]):
            return self._next_subtopic()

        if lower in ["yes", "ready", "ok", "sure", "let's go", "start"]:
            return self._start_teaching()

        # Generate Socratic response
        context = ""
        recent = self.session.state.get_recent_context(3)
        if recent:
            context = "\n".join(f"{ex['role']}: {ex['content']}" for ex in recent)

        response = self.content_gen.generate_socratic_response(
            subject=self.subject,
            subtopic=self.current_subtopic.get("name", self.subject) if self.current_subtopic else self.subject,
            learner_message=user_input,
            conversation_context=context,
            learner_level=self.profile.current_level,
        )

        return response

    def _next_subtopic(self) -> str:
        """Move to the next subtopic."""
        subtopics = self.topic_overview.get("subtopics", [])
        self.current_subtopic_index += 1

        if self.current_subtopic_index >= len(subtopics):
            return f"""You've covered all the main subtopics of {self.subject}!

Would you like to:
- Try some **practice** problems
- **Review** any topic
- Learn a **new subject**

What would you like to do?"""

        self.current_subtopic = subtopics[self.current_subtopic_index]
        self.lesson_content = self.content_gen.generate_lesson_content(
            self.subject,
            self.current_subtopic.get("name", ""),
            self.profile.current_level,
        )

        guiding_questions = self.lesson_content.get("guiding_questions", [])
        first_question = guiding_questions[0] if guiding_questions else f"What comes to mind when you think about {self.current_subtopic.get('name', 'this')}?"

        return f"""Great progress! Now let's explore **{self.current_subtopic.get('name', 'the next topic')}**.

{self.current_subtopic.get('description', '')}

{first_question}"""

    def _start_practice(self) -> str:
        """Start practice problems."""
        self.session.state.flow_state = "practice"

        subtopic_name = self.current_subtopic.get("name", self.subject) if self.current_subtopic else self.subject

        # Generate practice problems
        self.practice_problems = self.content_gen.generate_practice_problems(
            self.subject,
            subtopic_name,
            self.profile.current_level,
            count=3,
        )

        self.current_problem_index = 0
        self.hints_given = 0

        if not self.practice_problems:
            return "Let me generate some practice problems... Please try again in a moment."

        self.current_problem = self.practice_problems[0]

        return f"""Let's practice what you've learned about **{subtopic_name}**!

**Problem 1:**
{self.current_problem.get('question', '')}

Take your time. If you get stuck, just say **'hint'**."""

    def _handle_practice(self, user_input: str) -> str:
        """Handle practice problem responses."""
        if not self.current_problem:
            return self._start_practice()

        lower = user_input.lower().strip()

        # Check for hint request
        if lower in ["hint", "help", "stuck", "clue"]:
            hints = self.current_problem.get("hints", [])
            if self.hints_given < len(hints):
                hint = hints[self.hints_given]
                self.hints_given += 1
                return f"""Here's a hint: {hint}

Try again!"""
            else:
                return "I've given all my hints! Would you like me to explain the answer? Say 'show answer' or keep trying."

        # Check for give up
        if lower in ["give up", "answer", "show answer", "skip", "i don't know"]:
            explanation = self.current_problem.get("explanation", "")
            answer = self.current_problem.get("answer", "")

            self.session.record_problem(
                self.current_problem.get("id", "p1"), user_input, False, "gave up"
            )

            response = f"""No problem! The answer is: **{answer}**

{explanation}"""

            return response + "\n\n" + self._next_problem()

        # Evaluate the answer
        evaluation = self.content_gen.evaluate_answer(
            question=self.current_problem.get("question", ""),
            expected=self.current_problem.get("answer", ""),
            learner_answer=user_input,
            subject=self.subject,
        )

        if evaluation.get("correct"):
            self.session.record_problem(
                self.current_problem.get("id", "p1"), user_input, True, "correct"
            )

            # Update mastery
            current_mastery = self.profile.knowledge.topics_mastered.get(self.subject, 0)
            self.profile.update_mastery(self.subject, current_mastery + 15)
            self.learner_manager.save_learner(self.profile)

            explanation = self.current_problem.get("explanation", "")
            response = f"""Excellent! That's correct!

{explanation}"""

            return response + "\n\n" + self._next_problem()
        else:
            self.session.record_problem(
                self.current_problem.get("id", "p1"), user_input, False, "incorrect"
            )

            feedback = evaluation.get("feedback", "Not quite.")
            misconception = evaluation.get("misconception")

            response = f"{feedback}"
            if misconception:
                response += f" {misconception}"

            response += "\n\nTry again, or say **'hint'** for help!"
            return response

    def _next_problem(self) -> str:
        """Move to the next practice problem."""
        self.current_problem_index += 1
        self.hints_given = 0

        if self.current_problem_index >= len(self.practice_problems):
            # Summarize practice session
            correct = sum(1 for p in self.session.state.problems_attempted if p.get("correct"))
            total = len(self.session.state.problems_attempted)

            return f"""You've completed all practice problems!

Score: **{correct}/{total}**

Would you like to:
- Try **more** practice problems
- **Continue** learning the next topic
- Learn something **new**

What would you like to do?"""

        self.current_problem = self.practice_problems[self.current_problem_index]

        return f"""**Problem {self.current_problem_index + 1}:**
{self.current_problem.get('question', '')}

Take your time. Say **'hint'** if you need help."""

    def end_session(self) -> str:
        """End the current session and save progress."""
        if not self.session or not self.profile:
            return "No active session to end."

        summary = self.session.get_summary()
        self.profile.add_session_summary(summary)
        self.learner_manager.save_learner(self.profile)

        problems_done = summary.get("problems_attempted", 0)
        correct = summary.get("problems_correct", 0)

        message = f"""Great session learning about **{self.subject or 'your topic'}**!

Summary:
- Level: {self.profile.current_level}
- Problems attempted: {problems_done}"""

        if problems_done > 0:
            accuracy = (correct / problems_done) * 100
            message += f"\n- Problems correct: {correct} ({accuracy:.0f}%)"

        message += "\n\nYour progress has been saved. See you next time!"

        return message


# Alias for backwards compatibility
GeneticsTutor = DynamicTutor
