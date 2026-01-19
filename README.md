# Dynamic Learning Tutor

A personalized AI tutor that can teach **ANY topic** using the Socratic method. All content is generated dynamically based on the learner's chosen subject.

## Features

- **Learn Anything**: Just tell the tutor what you want to learn - Python, history, calculus, biology, music theory, anything!
- **Dynamic Content Generation**: All lessons, questions, and practice problems are generated on-the-fly using Claude
- **Adaptive Assessment**: Diagnoses your current level with dynamically generated questions
- **Socratic Teaching**: Guides learning through questions rather than lectures
- **Practice Problems**: Generated problems with hints and guided feedback
- **Progress Tracking**: Saves your progress across sessions

## How It Works

1. **Choose a Topic**: Tell the tutor what you want to learn
2. **Take Assessment**: Answer 5 questions to determine your level
3. **Learn Interactively**: Engage in Socratic dialogue about the subject
4. **Practice**: Test your knowledge with generated problems
5. **Progress**: Your learning is saved for next time

## Installation

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (uv will read from pyproject.toml)
uv pip install -e .

# Set your API key
export ANTHROPIC_API_KEY=your_key_here
```

## Usage

After installation, you can run the tutor in several ways:

**Option 1: Using the installed script (recommended)**
```bash
uv run tutor
```

**Option 2: Using uv run with Python**
```bash
uv run python main.py
```

**Option 3: Direct Python execution**
```bash
python main.py
```

Make sure you have set your `ANTHROPIC_API_KEY` environment variable before running.

### Example Session

```
What would you like to learn about today?
> I want to learn about machine learning

Great choice! Let's explore machine learning.
Here's what we'll cover:
  1. What is Machine Learning?
  2. Types of Learning (Supervised, Unsupervised, Reinforcement)
  3. Key Algorithms
  4. Training and Evaluation
  5. Practical Applications

First, let me ask you a few questions to understand what you already know...
```

### Commands

- `quit` / `exit` - End the session and save progress
- `practice` - Start practice problems
- `hint` - Get a hint (during practice)
- `skip` - Skip current question
- `next` - Move to the next subtopic
- `help` - Show available commands

## Project Structure

```
tutor-agent/
├── main.py                    # CLI entry point
├── agent/
│   ├── tutor.py              # Main dynamic tutoring agent
│   ├── content_generator.py  # Generates content using Claude
│   ├── prompts.py            # System prompts and templates
│   └── socratic.py           # Socratic questioning engine
├── state/
│   ├── storage.py            # JSON file persistence
│   ├── learner.py            # Learner profile management
│   └── session.py            # Session state tracking
├── data/
│   └── learners/             # Stored learner profiles
└── tests/
    └── ...
```

## Dynamic Content Generation

The tutor generates all content dynamically:

- **Topic Overview**: Subtopics, learning objectives, prerequisites
- **Assessment Questions**: 5 questions spanning beginner to advanced
- **Lesson Content**: Explanations, analogies, examples, guiding questions
- **Practice Problems**: Questions with hints and detailed explanations

This means you can learn about virtually any subject without pre-built content.

## Running Tests

```bash
pytest tests/ -v
```

## Technical Details

- **LLM**: Claude (via Anthropic API)
- **Storage**: JSON files for learner profiles
- **Caching**: Generated content is cached during session to reduce API calls
