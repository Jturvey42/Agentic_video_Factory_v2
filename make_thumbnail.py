# make_thumbnail.py
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def generate_production_thumbnail():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    output_path = os.path.join(base_dir, "output", "episode_2_thumbnail.jpg")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 1. Generate the exact data matrix from Episode 2
    total_steps = 30
    anomaly_index = 23
    dates = pd.date_range(start="2026-06-01", periods=total_steps, freq='D')
    
    np.random.seed(42)
    base_costs = 150.0 + np.random.normal(0, 4, total_steps)
    base_costs[anomaly_index] += 135.0  # The dramatic Z-score spike
    
    # 2. Setup high-contrast dark mode canvas (1920x1080 resolution)
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor('#0B0F19')  # Deep technical slate blue/black
    ax.set_facecolor('#0B0F19')
    
    # 3. Plot the telemetry timeline stream
    # Normal data line (up to the day before the anomaly)
    ax.plot(dates[:anomaly_index+1], base_costs[:anomaly_index+1], 
            color='#00E5FF', linewidth=5, alpha=0.9, label='Normal Telemetry')
    
    # Anomaly spike line
    ax.plot(dates[anomaly_index:anomaly_index+2], base_costs[anomaly_index:anomaly_index+2], 
            color='#FF1111', linewidth=6, alpha=1.0)
    
    # Remaining baseline stabilization trail
    ax.plot(dates[anomaly_index+1:], base_costs[anomaly_index+1:], 
            color='#00E5FF', linewidth=5, alpha=0.6)
    
    # 4. Plant the aggressive Anomaly Marker
    ax.scatter(dates[anomaly_index], base_costs[anomaly_index], 
               color='#FF1111', s=350, edgecolors='white', linewidths=3, zorder=5)
    
    # 5. Dynamic HUD Label Overlays (Arrests the viewer's eye)
    # Huge prominent Title text
    ax.text(0.05, 0.88, "CLOUD COST ANOMALY DETECTED", 
            transform=ax.transAxes, fontsize=32, fontweight='bold', fontname='Courier New', color='#FF1111')
    
    # Z-Score metric indicator
    ax.text(0.05, 0.80, "CRITICAL METRIC: Z-SCORE 3.12", 
            transform=ax.transAxes, fontsize=20, fontname='Courier New', color='#00E5FF')
    
    # 6. Formatting axis lines for technical clarity
    ax.set_title("ENTERPRISE INFRASTRUCTURE FEE TELEMETRY LOGS", 
                 fontsize=14, pad=20, fontname='Courier New', color='#AEB7C6', alpha=0.7)
    ax.set_ylabel("Daily Spend Rate (USD)", fontsize=16, fontname='Courier New', color='#AEB7C6')
    ax.grid(True, linestyle='--', alpha=0.15, color='#FFFFFF')
    
    # Set rigid bounds so the framing is perfectly balanced
    ax.set_ylim(50, 350)
    ax.tick_params(axis='both', which='major', labelsize=12, colors='#AEB7C6')
    
    # Clean up outer borders
    for spine in ['top', 'right', 'left', 'bottom']:
        ax.spines[spine].set_color('#1E293B')
        ax.spines[spine].set_alpha(0.5)
        
    plt.tight_layout()
    
    # Save the high-resolution master asset
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
    plt.close()
    print(f"[SUCCESS] Production-ready thumbnail generated at: {output_path}")

if __name__ == "__main__":
    generate_production_thumbnail()