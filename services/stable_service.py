import datetime
from pathlib import Path
from typing import Dict, Any, List
from utils.file_handler import FileHandler
from services.history_service import HistoryService
from services.prediction_service import PredictionService


class StableService:
    """Service for managing stable data (current and predicted events)."""

    def __init__(self, file_handler: FileHandler, stable_file: Path,
                 history_service: HistoryService, prediction_service: PredictionService):
        self.file_handler = file_handler
        self.stable_file = stable_file
        self.history_service = history_service
        self.prediction_service = prediction_service
        self.current_time = datetime.datetime.now().timestamp() * 1000

    def get_stable_data(self) -> Dict[str, Any]:
        """Get current stable data."""
        return self.file_handler.load_json(self.stable_file) or {"current": {}, "predicted": []}

    def update_stable_data(self) -> bool:
        """Update stable data with current and predicted events."""
        stable = self.get_stable_data()
        current_data = stable["current"]

        if "datetime_utc" in current_data:
            current_timestamp = current_data["datetime_utc"]
            is_predicted = current_data.get("predicted", False)

            if not is_predicted:
                self.history_service.append_timestamp(current_timestamp)

            if current_timestamp < self.current_time:
                stable["current"] = {}

        if not stable["current"] and stable["predicted"]:
            stable["current"] = stable["predicted"].pop(0)

        return self.file_handler.save_json(self.stable_file, stable)

    def fill_closest_predictions(self, max_predictions: int = 5, min_time_diff_days: int = 3) -> bool:
        """Fill stable file with closest future predictions."""
        stable = self.get_stable_data()
        future_predictions = self.prediction_service.get_future_predictions(self.current_time)

        if not future_predictions:
            return True

        stable["predicted"] = future_predictions[:max_predictions]

        current_data = stable["current"]
        if "datetime_utc" in current_data and future_predictions:
            current_timestamp = current_data["datetime_utc"]
            first_predicted_timestamp = future_predictions[0]["datetime_utc"]

            time_difference_days = (first_predicted_timestamp - current_timestamp) / (24 * 3600 * 1000)

            if time_difference_days < min_time_diff_days and len(future_predictions) > max_predictions:
                stable["predicted"] = future_predictions[1:max_predictions + 1]

        return self.file_handler.save_json(self.stable_file, stable)
