from pathlib import Path
from utils.file_handler import FileHandler
from services.history_service import HistoryService
from services.prediction_service import PredictionService
from services.stable_service import StableService


class TimeSeriesPredictionPipeline:
    """Main pipeline orchestrator for time series prediction."""

    def __init__(self, data_dir: str = './data'):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # File paths
        self.stable_file = self.data_dir / 'stable.json'
        self.history_file = self.data_dir / 'history.json'
        self.predicted_file = self.data_dir / 'predicted.json'

        # Initialize services
        self.file_handler = FileHandler()
        self.history_service = HistoryService(self.file_handler, self.history_file)
        self.prediction_service = PredictionService(self.file_handler, self.predicted_file, self.history_service)
        self.stable_service = StableService(self.file_handler, self.stable_file,
                                          self.history_service, self.prediction_service)

    def run(self) -> bool:
        """Run the complete prediction pipeline."""
        try:
            print("Starting prediction pipeline...")

            print("Updating stable data...")
            if not self.stable_service.update_stable_data():
                print("Failed to update stable data")
                return False

            print("Generating predictions...")
            if not self.prediction_service.generate_predictions():
                print("Failed to generate predictions")
                return False

            print("Filling closest predictions...")
            if not self.stable_service.fill_closest_predictions():
                print("Failed to fill closest predictions")
                return False

            print("Prediction pipeline completed successfully")
            return True

        except Exception as e:
            print(f"Error in prediction pipeline: {e}")
            return False


def main():
    """Main execution function."""
    pipeline = TimeSeriesPredictionPipeline()
    success = pipeline.run()

    if not success:
        exit(1)


if __name__ == "__main__":
    main()
