"""Topic definitions and hierarchy for genetics curriculum."""

from typing import Optional

# Topic hierarchy for genetics curriculum
TOPIC_HIERARCHY = {
    "dna_basics": {
        "id": "dna_basics",
        "name": "DNA Basics",
        "level": "beginner",
        "prerequisites": [],
        "subtopics": ["dna_structure", "nucleotides", "base_pairing"],
        "description": "Understanding the structure and components of DNA",
    },
    "mendelian_inheritance": {
        "id": "mendelian_inheritance",
        "name": "Mendelian Inheritance",
        "level": "beginner",
        "prerequisites": ["dna_basics"],
        "subtopics": ["dominant_recessive", "genotype_phenotype", "alleles"],
        "description": "Mendel's laws of inheritance and basic genetic patterns",
    },
    "punnett_squares": {
        "id": "punnett_squares",
        "name": "Punnett Squares",
        "level": "beginner",
        "prerequisites": ["mendelian_inheritance"],
        "subtopics": ["monohybrid_cross", "dihybrid_cross", "probability"],
        "description": "Using Punnett squares to predict genetic outcomes",
    },
    "pedigree_analysis": {
        "id": "pedigree_analysis",
        "name": "Pedigree Analysis",
        "level": "intermediate",
        "prerequisites": ["punnett_squares"],
        "subtopics": ["inheritance_patterns", "carrier_identification"],
        "description": "Analyzing family trees to track inheritance patterns",
    },
    "molecular_genetics": {
        "id": "molecular_genetics",
        "name": "Molecular Genetics",
        "level": "intermediate",
        "prerequisites": ["dna_basics"],
        "subtopics": ["replication", "transcription", "translation"],
        "description": "DNA replication and protein synthesis",
    },
    "gene_expression": {
        "id": "gene_expression",
        "name": "Gene Expression",
        "level": "advanced",
        "prerequisites": ["molecular_genetics"],
        "subtopics": ["regulation", "epigenetics"],
        "description": "How genes are turned on and off",
    },
    "mutations": {
        "id": "mutations",
        "name": "Mutations & Genetic Diseases",
        "level": "advanced",
        "prerequisites": ["molecular_genetics", "pedigree_analysis"],
        "subtopics": ["types_of_mutations", "genetic_disorders"],
        "description": "Types of mutations and their effects on health",
    },
}

# Suggested learning path by level
LEARNING_PATHS = {
    "beginner": ["dna_basics", "mendelian_inheritance", "punnett_squares"],
    "intermediate": ["pedigree_analysis", "molecular_genetics"],
    "advanced": ["gene_expression", "mutations"],
}


def get_topic(topic_id: str) -> Optional[dict]:
    """Get topic information by ID."""
    return TOPIC_HIERARCHY.get(topic_id)


def get_prerequisites(topic_id: str) -> list[str]:
    """Get prerequisite topics for a given topic."""
    topic = get_topic(topic_id)
    if topic is None:
        return []
    return topic.get("prerequisites", [])


def get_next_topic(current_topic: str, mastered_topics: list[str]) -> Optional[str]:
    """Suggest the next topic based on current progress."""
    current = get_topic(current_topic)
    if current is None:
        return "dna_basics"  # Default starting point

    # Find topics that have current topic as prerequisite
    for topic_id, topic in TOPIC_HIERARCHY.items():
        if topic_id in mastered_topics:
            continue
        if current_topic in topic.get("prerequisites", []):
            # Check if all prerequisites are met
            prereqs = topic.get("prerequisites", [])
            if all(p in mastered_topics or p == current_topic for p in prereqs):
                return topic_id

    # If no next topic found, suggest based on level
    current_level = current.get("level", "beginner")
    level_index = {"beginner": 0, "intermediate": 1, "advanced": 2}
    idx = level_index.get(current_level, 0)

    # Try same level first, then next level
    for level in list(level_index.keys())[idx:]:
        for topic_id in LEARNING_PATHS.get(level, []):
            if topic_id not in mastered_topics:
                return topic_id

    return None  # All topics mastered!


def get_topics_for_level(level: str) -> list[str]:
    """Get all topic IDs appropriate for a given level."""
    return LEARNING_PATHS.get(level, [])
