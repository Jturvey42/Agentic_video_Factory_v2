# src/chart_overlay_engine.py
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class TelemetryChartEngine:
    def __init__(self, output_dir: str = "output/chart_frames", resolution: tuple = (1920, 1080)):
        self.output_dir = output_dir
        self.resolution = resolution
        self.dpi = 100
        os.makedirs(self.output_dir, exist_ok=True)
        plt.style.use('dark_background')
        
    def render_sequenced_frames(self, telemetry_df: pd.DataFrame, fps: int = 30, secs_per_day: float = 1.0):
        print(f"[VISUAL] Generating sequenced economic chart frames at {fps} FPS...")
        
        # Clean old frame cache safely
        for f in os.listdir(self.output_dir):
            if f.endswith('.png'):
                try: 
                    os.remove(os.path.join(self.output_dir, f))
                except: 
                    pass

        total_days = len(telemetry_df)
        total_frames = int(total_days * secs_per_day * fps)
        frames_per_day = fps * secs_per_day
        
        fig, ax = plt.subplots(figsize=(self.resolution[0]/self.dpi, self.resolution[1]/self.dpi), dpi=self.dpi)
        
        # Look for the economic shock event trigger point
        anomaly_rows = telemetry_df[telemetry_df['is_anomaly'] == True]
        anomaly_idx = anomaly_rows.index[0] if not anomaly_rows.empty else 9999
        
        min_date = telemetry_df['log_timestamp'].min()
        max_date = telemetry_df['log_timestamp'].max()

        # Dynamic calculation of Y limits to adapt gracefully to global freight scale jumps
        min_y = float(telemetry_df['infrastructure_fee_usd'].min() * 0.85)
        max_y = float(telemetry_df['infrastructure_fee_usd'].max() * 1.15)

        for frame_idx in range(total_frames):
            ax.clear()
            
            current_day_float = frame_idx / frames_per_day
            current_day_idx = min(int(np.floor(current_day_float)), total_days - 1)
            
            visible_data = telemetry_df.iloc[:max(1, current_day_idx + 1)]
            
            fig.patch.set_facecolor('#141417') 
            ax.set_facecolor('#141417')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, color='#2A2A35', linestyle='--', alpha=0.4)
            
            # Switch color scheme from calm cyan to high-alert crimson once the chokepoint closes
            has_anomaly_hit = current_day_idx >= anomaly_idx
            line_color = '#FF3366' if has_anomaly_hit else '#00E5FF' 
            
            if len(visible_data) > 0:
                ax.plot(
                    visible_data['log_timestamp'], 
                    visible_data['infrastructure_fee_usd'], 
                    color=line_color, 
                    linewidth=4.0
                )
            
            current_active_row = telemetry_df.iloc[current_day_idx]
            node_radius = 15 if current_active_row['is_anomaly'] else 8
            node_color = '#FF1111' if current_active_row['is_anomaly'] else '#00E5FF'
            
            ax.scatter(
                current_active_row['log_timestamp'],
                current_active_row['infrastructure_fee_usd'],
                color=node_color,
                s=node_radius ** 2,
                zorder=5
            )
            
            ax.set_xlim(min_date, max_date)
            ax.set_ylim(min_y, max_y)
            
            # Re-label typography for the Global Supply Shock scenario
            ax.set_title("SYSTEMIC TELEMETRY: MARITIME CHOKEPOINT CAPACITY SHOCK", fontsize=16, color='#8E8E9F', pad=20, fontname="Courier New")
            ax.set_ylabel("Global Container Freight Index ($ / FEU)", fontsize=12, color='#8E8E9F', fontname="Courier New")
            
            frame_path = os.path.join(self.output_dir, f"frame_{frame_idx:04d}.png")
            plt.savefig(frame_path, facecolor=fig.get_facecolor(), edgecolor='none', bbox_inches='tight')
                
        plt.close()
        print(f"[VISUAL] Sequence rendering complete. Saved to {self.output_dir}")
        return self.output_dir