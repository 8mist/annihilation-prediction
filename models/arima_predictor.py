import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tools.sm_exceptions import ConvergenceWarning
import warnings
from typing import List, Optional, Dict, Any, Tuple

warnings.simplefilter('ignore', ConvergenceWarning)


class ARIMAPredictor:
    """ARIMA model for time series prediction."""

    def __init__(self, order: tuple = (1, 1, 1)):
        self.order = order
        self.model = None
        self.fitted_model = None

    def prepare_data(self, history_data: List[Dict[str, Any]]) -> Optional[Tuple[pd.Series, pd.Timestamp]]:
        """Prepare historical data for ARIMA modeling."""
        if not history_data or len(history_data) < 3:
            print("Insufficient historical data for prediction")
            return None

        df = pd.DataFrame(history_data)
        df['datetime_utc'] = pd.to_datetime(df['datetime_utc'], unit='ms')
        df.sort_values('datetime_utc', inplace=True)
        df.reset_index(drop=True, inplace=True)

        df['diff_days'] = df['datetime_utc'].diff().dt.total_seconds() / 86400

        diff_series = df['diff_days'].dropna()

        if len(diff_series) < 2:
            print("Insufficient data points for time series analysis")
            return None

        diff_series.index = pd.date_range(
            start=df['datetime_utc'].iloc[1],
            periods=len(diff_series),
            freq='D'
        )

        return diff_series, df['datetime_utc'].iloc[-1]

    def fit(self, series: pd.Series) -> bool:
        """Fit ARIMA model to the time series."""
        try:
            self.model = ARIMA(series, order=self.order)
            self.fitted_model = self.model.fit()
            return True
        except Exception as e:
            print(f"Error fitting ARIMA model: {e}")
            return False

    def forecast(self, steps: int = 10) -> Optional[pd.Series]:
        """Generate forecasts using fitted model."""
        if self.fitted_model is None:
            print("Model not fitted. Call fit() first.")
            return None

        try:
            return self.fitted_model.forecast(steps=steps)
        except Exception as e:
            print(f"Error generating forecasts: {e}")
            return None

    def predict_timestamps(self, history_data: List[Dict[str, Any]], steps: int = 10) -> Optional[List[Dict[str, Any]]]:
        """Generate predicted timestamps."""
        result = self.prepare_data(history_data)
        if result is None:
            return None

        diff_series, last_event_date = result

        if not self.fit(diff_series):
            return None

        forecast_intervals = self.forecast(steps)
        if forecast_intervals is None:
            return None

        cumulative_intervals = forecast_intervals.cumsum()
        predicted_data = [
            {
                "datetime_utc": int((last_event_date + pd.Timedelta(days=interval)).timestamp() * 1000),
                "predicted": True
            }
            for interval in cumulative_intervals
        ]

        return predicted_data
