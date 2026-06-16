# financial_sentinel.py
import pandas as pd
import numpy as np

class FinancialSentinel:
    def __init__(self, window_size: int = 7, threshold: float = 2.0):
        """
        Initializes the analytical parameters for anomaly detection.
        """
        self.window_size = window_size
        self.threshold = threshold

    def process_cost_telemetry(self, raw_log_df: pd.DataFrame, timestamp_col: str, cost_col: str) -> pd.DataFrame:
        """
        Ingests infrastructure data, aggregates to daily spend, 
        and calculates rolling Z-scores without look-ahead bias.
        """
        # Isolate work columns on a fresh copy to prevent SettingWithCopyWarnings
        df = raw_log_df[[timestamp_col, cost_col]].copy()
        
        # Enforce true datetime types and sort chronologically
        df[timestamp_col] = pd.to_datetime(df[timestamp_col])
        df = df.sort_values(by=timestamp_col)
        
        # Resample data to clean, continuous daily bins, summing multiple infra charges per day
        daily_spend = df.set_index(timestamp_col).resample('D').sum().reset_index()
        
        # Pre-allocate numpy arrays for performance and precise index matching
        total_intervals = len(daily_spend)
        rolling_mean = np.zeros(total_intervals)
        rolling_std = np.zeros(total_intervals)
        z_scores = np.zeros(total_intervals)
        
        # Chronological scoring loop
        for i in range(total_intervals):
            # Window management: expand window early on, switch to sliding window later
            if i < self.window_size:
                historical_slice = daily_spend[cost_col].iloc[0:i+1]
            else:
                historical_slice = daily_spend[cost_col].iloc[i - self.window_size + 1: i + 1]
                
            mean = historical_slice.mean()
            std = historical_slice.std()
            
            rolling_mean[i] = mean
            # Inject small epsilon guard if standard deviation is absolute zero
            rolling_std[i] = std if std > 0 else 1e-6
            
            # Calculate standard deviations away from the historical mean
            z_scores[i] = (daily_spend[cost_col].iloc[i] - rolling_mean[i]) / rolling_std[i]

        # Attach computed arrays directly back to the structured DataFrame
        daily_spend['rolling_mean'] = rolling_mean
        daily_spend['rolling_std'] = rolling_std
        daily_spend['z_score'] = z_scores
        
        # Flag anomalies where the absolute Z-score crosses the statistical threshold boundary
        daily_spend['is_anomaly'] = np.abs(daily_spend['z_score']) > self.threshold
        
        return daily_spend