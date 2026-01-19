"""Persistence layer for learner data using JSON files."""

import json
import os
from pathlib import Path
from typing import Optional
from datetime import datetime


class Storage:
    """Handles reading and writing learner data to JSON files."""

    def __init__(self, data_dir: str = "data/learners"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def _get_learner_path(self, learner_id: str) -> Path:
        """Get the file path for a learner's data."""
        return self.data_dir / f"{learner_id}.json"

    def save_learner(self, learner_id: str, data: dict) -> None:
        """Save learner data to a JSON file."""
        path = self._get_learner_path(learner_id)
        data["updated_at"] = datetime.now().isoformat()
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def load_learner(self, learner_id: str) -> Optional[dict]:
        """Load learner data from a JSON file. Returns None if not found."""
        path = self._get_learner_path(learner_id)
        if not path.exists():
            return None
        with open(path, "r") as f:
            return json.load(f)

    def learner_exists(self, learner_id: str) -> bool:
        """Check if a learner profile exists."""
        return self._get_learner_path(learner_id).exists()

    def list_learners(self) -> list[str]:
        """List all learner IDs."""
        return [p.stem for p in self.data_dir.glob("*.json")]

    def delete_learner(self, learner_id: str) -> bool:
        """Delete a learner's data file."""
        path = self._get_learner_path(learner_id)
        if path.exists():
            path.unlink()
            return True
        return False
