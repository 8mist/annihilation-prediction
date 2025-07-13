from pathlib import Path
from typing import List, Dict, Any, Optional
from utils.file_handler import FileHandler
from models.arima_predictor import ARIMAPredictor
from services.history_service import HistoryService


class PredictionService:
    """Service for generating and managing predictions."""

    def __init__(self, file_handler: FileHandler, predicted_file: Path, history_service: HistoryService):
        self.file_handler = file_handler
        self.predicted_file = predicted_file
        self.history_service = history_service
        self.predictor = ARIMAPredictor()

    def generate_predictions(self, steps: int = 10) -> bool:
        """Generate predictions using historical data."""
        if not self.history_service.has_sufficient_data():
            print("Insufficient historical data for prediction")
            return False

        history_data = self.history_service.get_history()
        predicted_data = self.predictor.predict_timestamps(history_data, steps)

        if predicted_data is None:
            return False

        return self.file_handler.save_json(self.predicted_file, predicted_data)

    def get_predictions(self) -> List[Dict[str, Any]]:
        """Get current predictions."""
        return self.file_handler.load_json(self.predicted_file) or []

    def get_future_predictions(self, current_time: float) -> List[Dict[str, Any]]:
        """Get predictions that are in the future."""
        predictions = self.get_predictions()
        return sorted(
            [item for item in predictions if item["datetime_utc"] > current_time],
            key=lambda x: x["datetime_utc"]
        )
