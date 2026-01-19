"""Question bank for diagnostic assessment."""

DIAGNOSTIC_QUESTIONS = [
    {
        "id": "diag_001",
        "level": "beginner",
        "question": "What molecule carries genetic information in living things?",
        "answer": "DNA",
        "acceptable_answers": ["dna", "deoxyribonucleic acid"],
        "topic": "dna_basics",
        "follow_up_if_wrong": "diag_001b",
    },
    {
        "id": "diag_001b",
        "level": "beginner",
        "question": "Have you heard of DNA before? It stands for deoxyribonucleic acid. What do you think DNA does in your body?",
        "answer": "open_ended",
        "acceptable_patterns": ["instruction", "code", "information", "genes", "traits", "heredit", "blueprint"],
        "topic": "dna_basics",
        "is_followup": True,
    },
    {
        "id": "diag_002",
        "level": "beginner",
        "question": "If brown eyes (B) are dominant over blue eyes (b), what eye color would someone with genotype 'Bb' have?",
        "answer": "brown",
        "acceptable_answers": ["brown", "brown eyes"],
        "topic": "mendelian_inheritance",
        "follow_up_if_wrong": "diag_002b",
    },
    {
        "id": "diag_002b",
        "level": "beginner",
        "question": "Do you know what 'dominant' and 'recessive' mean in genetics?",
        "answer": "open_ended",
        "acceptable_patterns": ["dominant shows", "dominant wins", "recessive hidden", "recessive needs two", "masks"],
        "topic": "mendelian_inheritance",
        "is_followup": True,
    },
    {
        "id": "diag_003",
        "level": "intermediate",
        "question": "If two parents with genotype Bb have children, what percentage of their children would you expect to have genotype bb?",
        "answer": "25%",
        "acceptable_answers": ["25%", "25", "1/4", "one fourth", "one quarter", "25 percent"],
        "topic": "punnett_squares",
        "follow_up_if_wrong": "diag_003b",
    },
    {
        "id": "diag_003b",
        "level": "intermediate",
        "question": "Have you used Punnett squares before to predict offspring traits?",
        "answer": "open_ended",
        "acceptable_patterns": ["yes", "learned", "grid", "square", "cross"],
        "topic": "punnett_squares",
        "is_followup": True,
    },
    {
        "id": "diag_004",
        "level": "intermediate",
        "question": "What is the term for different versions of the same gene, like B and b for eye color?",
        "answer": "alleles",
        "acceptable_answers": ["allele", "alleles"],
        "topic": "mendelian_inheritance",
    },
    {
        "id": "diag_005",
        "level": "advanced",
        "question": "Two brown-eyed parents have a blue-eyed child. What must be true about the parents' genotypes?",
        "answer": "Both must be heterozygous (Bb)",
        "acceptable_answers": ["bb", "heterozygous", "Bb", "both Bb", "both heterozygous", "carriers"],
        "topic": "punnett_squares",
    },
]

# Mapping for adaptive assessment flow
QUESTION_SEQUENCE = {
    "start": "diag_001",
    "diag_001": {"correct": "diag_002", "wrong": "diag_001b"},
    "diag_001b": {"next": "diag_002"},
    "diag_002": {"correct": "diag_003", "wrong": "diag_002b"},
    "diag_002b": {"next": "diag_003"},
    "diag_003": {"correct": "diag_005", "wrong": "diag_003b"},  # Skip to advanced if correct
    "diag_003b": {"next": "diag_004"},
    "diag_004": {"correct": "diag_005", "wrong": "end"},
    "diag_005": {"correct": "end", "wrong": "end"},
}


def get_question(question_id: str) -> dict | None:
    """Get a question by its ID."""
    for q in DIAGNOSTIC_QUESTIONS:
        if q["id"] == question_id:
            return q
    return None


def get_first_question() -> dict:
    """Get the first diagnostic question."""
    return get_question(QUESTION_SEQUENCE["start"])


def get_next_question(current_id: str, was_correct: bool) -> dict | None:
    """Get the next question based on current answer correctness."""
    if current_id not in QUESTION_SEQUENCE:
        return None

    next_mapping = QUESTION_SEQUENCE[current_id]

    if "next" in next_mapping:
        # This is a follow-up question, just go to next
        next_id = next_mapping["next"]
    elif was_correct:
        next_id = next_mapping.get("correct", "end")
    else:
        next_id = next_mapping.get("wrong", "end")

    if next_id == "end":
        return None

    return get_question(next_id)
