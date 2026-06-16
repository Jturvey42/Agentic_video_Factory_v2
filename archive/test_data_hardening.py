# test_data_hardening.py
import pandas as pd
import numpy as np
from financial_sentinel import FinancialSentinel

def run_step_function_analysis():
    print("=== STEP 3: DATA HARDENING & STEP-FUNCTION ANALYSIS ===")
    
    # 1. Create a 30-day timeline
    dates = pd.date_range(start="2026-06-01", periods=30, freq='D')
    
    # 2. Build a data array that permanently steps up on Day 11
    # Days 1-10: Stable around $150
    # Days 11-30: Permanently jumps to stable $300 due to database migration
    costs = np.zeros(30)
    np.random.seed(42)
    noise = np.random.normal(loc=0, scale=2, size=30)
    
    for i in range(30):
        if i < 10:
            costs[i] = 150.0 + noise[i]
        else:
            costs[i] = 300.0 + noise[i] # The permanent step-up event
            
    mock_logs = pd.DataFrame({
        'log_timestamp': dates,
        'infrastructure_fee_usd': costs
    })
    
    # 3. Process with our 7-day lookback sentinel
    sentinel = FinancialSentinel(window_size=7, threshold=2.0)
    processed_telemetry = sentinel.process_cost_telemetry(
        raw_log_df=mock_logs, 
        timestamp_col='log_timestamp', 
        cost_col='infrastructure_fee_usd'
    )
    
    # 4. Filter and display the critical window (Days 8 through 18) to observe the transition
    columns_to_show = ['log_timestamp', 'infrastructure_fee_usd', 'z_score', 'is_anomaly']
    print(processed_telemetry[columns_to_show].iloc[7:18].to_string(index=False))

if __name__ == "__main__":
    run_step_function_analysis()