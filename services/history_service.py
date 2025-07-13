import datetime
from pathlib import Path
from typing import List, Dict, Any
from utils.file_handler import FileHandler


class HistoryService:
    """Service for managing historical data."""

    def __init__(self, file_handler: FileHandler, history_file: Path):
        self.file_handler = file_handler
        self.history_file = history_file

    def get_history(self) -> List[Dict[str, Any]]:
        """Get historical data."""
        return self.file_handler.load_json(self.history_file, use_cache=False) or []

    def append_timestamp(self, timestamp: float) -> bool:
        """Append timestamp to history if not already present."""
        history = self.get_history()

        existing_timestamps = {item["datetime_utc"] for item in history}

        if timestamp not in existing_timestamps:
            history.append({"datetime_utc": timestamp})
            return self.file_handler.save_json(self.history_file, history)

        return True

    def has_sufficient_data(self, min_points: int = 3) -> bool:
        """Check if we have sufficient historical data."""
        history = self.get_history()
        return len(history) >= min_points
