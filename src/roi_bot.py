import os
import sys
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATION & PATHS ---
PROJECT_ROOT = "E:/Agentic_Video_Factory_v2"
CSV_PATH = os.path.join(PROJECT_ROOT, "data/cloud_spend.csv")
OUTPUT_CHART_PATH = os.path.join(PROJECT_ROOT, "assets/roi_output.png")

def validate_environment():
    """Guardrail: Validates existence of data directories and files."""
    if not os.path.exists(CSV_PATH):
        print(f"[ERROR] Target data asset missing at: {CSV_PATH}")
        print("[RISK] Pipeline termination prevented. Please place the cloud_spend.csv file in the data/ directory.")
        sys.exit(1)
    
    # Ensure artifacts directory exists for output
    os.makedirs(os.path.dirname(OUTPUT_CHART_PATH), exist_ok=True)

def generate_roi_chart():
    validate_environment()
    
    print("[LOG] Initializing Math Bot Data Parsing...")
    try:
        # Load data
        df = pd.read_csv(CSV_PATH)
        
        # Guardrail: Check for empty dataset
        if df.empty:
            raise ValueError("The cloud_spend.csv file is empty.")
            
        # Guardrail: Validate required columns
        required_cols = {'Month', 'Unoptimized_Spend', 'Optimized_Spend'}
        if not required_cols.issubset(df.columns):
            raise KeyError(f"Missing required columns. CSV must contain: {required_cols}")

        print("[LOG] Data validation passed. Calculating financial metrics...")
        
        # Financial Calculations (Strict rounding to 2 decimal places)
        df['Savings'] = df['Unoptimized_Spend'] - df['Optimized_Spend']
        total_unoptimized = round(df['Unoptimized_Spend'].sum(), 2)
        total_optimized = round(df['Optimized_Spend'].sum(), 2)
        total_savings = round(df['Savings'].sum(), 2)
        
        print(f"--- MATH BOT REPORT ---")
        print(f"Baseline Spend: ${total_unoptimized:,}")
        print(f"Optimized Spend: ${total_optimized:,}")
        print(f"Net Pipeline Savings: ${total_savings:,}")
        print(f"-----------------------")

        # --- PLOTLY VIDEO ASSET GENERATION ---
        print("[LOG] Generating high-contrast static video asset...")
        fig = go.Figure()

        # Unoptimized Spend Trend Line
        fig.add_trace(go.Scatter(
            x=df['Month'], 
            y=df['Unoptimized_Spend'],
            mode='lines+markers',
            name='Principal Investment Baseline',
            line=dict(color='#FF4B4B', width=4, dash='dash'),
            marker=dict(size=8)
        ))

        # Optimized Spend Trend Line
        fig.add_trace(go.Scatter(
            x=df['Month'], 
            y=df['Optimized_Spend'],
            mode='lines+markers',
            name='Active Portfolio Value',
            line=dict(color='#00CC96', width=4),
            marker=dict(size=8)
        ))

        # Apply Video Layout Specifications (1080p legibility, dark theme for video production)
        fig.update_layout(
            template="plotly_dark",
            title={
                'text': "Strategic Asset Growth & ROI Trajectory",
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top',
                'font': dict(size=24, family="Arial", color="#FFFFFF")
            },
            xaxis=dict(
                title="Timeline", 
                gridcolor="#444444", 
                tickfont=dict(size=14)
            ),
           yaxis=dict(
                title="Total Portfolio Valuation ($)", 
                gridcolor="#444444", 
                tickfont=dict(size=14)
            ),
            legend=dict(
                orientation="h", 
                yanchor="bottom", 
                y=1.02, 
                xanchor="right", 
                x=1,
                font=dict(size=14)
            ),
            width=960,
            height=1080,
            margin=dict(l=80, r=80, t=120, b=80)
        )

        # Guardrail: Requires 'kaleido' package to save as static PNG
        fig.write_image(OUTPUT_CHART_PATH, engine="kaleido")
        print(f"[SUCCESS] Static chart asset written to: {OUTPUT_CHART_PATH}")

    except Exception as e:
        print(f"[CRITICAL ERROR] Math Bot Pipeline failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    generate_roi_chart()