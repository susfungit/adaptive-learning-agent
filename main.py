#!/usr/bin/env python3
"""
Dynamic Tutoring Agent - CLI Interface

A personalized tutor that can teach ANY topic using the Socratic method.
All content is generated dynamically based on the learner's chosen subject.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.tutor import DynamicTutor


def print_wrapped(text: str, width: int = 80) -> None:
    """Print text with simple word wrapping."""
    lines = text.split('\n')
    for line in lines:
        if len(line) <= width:
            print(line)
        else:
            words = line.split()
            current = []
            current_len = 0
            for word in words:
                if current_len + len(word) + 1 <= width:
                    current.append(word)
                    current_len += len(word) + 1
                else:
                    print(' '.join(current))
                    current = [word]
                    current_len = len(word)
            if current:
                print(' '.join(current))


def get_learner_info() -> tuple[str, str]:
    """Get learner ID and name from user."""
    print("\n" + "=" * 60)
    print("        Welcome to the Dynamic Learning Tutor")
    print("       Learn ANY topic through guided discovery!")
    print("=" * 60 + "\n")

    learner_id = input("Enter your username (or 'new' to create): ").strip()

    if learner_id.lower() == 'new':
        learner_id = input("Choose a username: ").strip()
        name = input("What's your name? ").strip()
        return learner_id, name

    return learner_id, None


def main():
    """Main entry point for the tutoring agent."""
    try:
        learner_id, name = get_learner_info()

        if not learner_id:
            print("Username required. Exiting.")
            return

        # Initialize tutor
        print("\nStarting session...\n")
        tutor = DynamicTutor()

        # Start session
        welcome = tutor.start_session(learner_id, name)
        print("-" * 60)
        print_wrapped(welcome)
        print("-" * 60)

        # Main interaction loop
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue

                # Check for exit commands
                if user_input.lower() in ['quit', 'exit', 'bye', 'done', 'end']:
                    goodbye = tutor.end_session()
                    print("\n" + "-" * 60)
                    print_wrapped(goodbye)
                    print("-" * 60)
                    break

                # Check for help command
                if user_input.lower() == 'help':
                    print("""
Commands:
  'quit' or 'exit'  - End the session and save progress
  'practice'        - Start practice problems
  'hint'            - Get a hint (during practice)
  'skip'            - Skip current question
  'next'            - Move to the next subtopic
  'help'            - Show this help message

During learning, just type naturally - the tutor will guide you!
""")
                    continue

                # Get tutor response
                response = tutor.handle_input(user_input)
                print("\n" + "-" * 60)
                print("Tutor:", end=" ")
                print_wrapped(response)
                print("-" * 60)

            except KeyboardInterrupt:
                print("\n\nSession interrupted.")
                goodbye = tutor.end_session()
                print_wrapped(goodbye)
                break

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure you have set the ANTHROPIC_API_KEY environment variable.")
        sys.exit(1)


if __name__ == "__main__":
    main()
