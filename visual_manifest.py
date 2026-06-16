# visual_manifest.py
import pandas as pd
import numpy as np

class VisualManifestGenerator:
    def __init__(self, fps: int = 30, scale_factor: float = 1.0):
        """
        Translates raw analytical telemetry data into structural video events,
        resolving dynamic styling and asset triggers frame-by-frame.
        """
        self.fps = fps
        self.scale_factor = scale_factor

    def generate_scene_manifest(self, telemetry_df: pd.DataFrame) -> list:
        """
        Iterates over the telemetry matrix and generates a timeline dictionary
        for every second of the video clip based on data spikes.
        """
        scene_events = []
        
        # Define base layout boundaries (1920x1080 canvas coordinates)
        base_layout = {
            "canvas_width": 1920,
            "canvas_height": 1080,
            "chart_box": {"x": 200, "y": 300, "w": 1520, "h": 500}
        }

        for idx, row in telemetry_df.iterrows():
            timestamp_str = row['log_timestamp'].strftime('%Y-%m-%d')
            cost = float(row['infrastructure_fee_usd'])
            z_score = float(row['z_score'])
            is_anomaly = bool(row['is_anomaly'])

            # 1. Dynamic Styling: Switch UI theme colors programmatically based on anomalies
            if is_anomaly:
                primary_color = "#FF3333"  # Critical Crimson Warning
                bg_alert_intensity = min(1.0, abs(z_score) / 4.0)  # Scale background glow with spike severity
                text_effect = "shake_heavy"
                narration_cue = "DUCK_AUDIO_LOW" # Tells the audio mixer to clamp background tracks aggressively
            else:
                primary_color = "#00FFCC"  # Stable Terminal Cyan
                bg_alert_intensity = 0.0
                text_effect = "none"
                narration_cue = "DUCK_AUDIO_NORMAL"

            # 2. Frame Manifest Assignment
            frame_state = {
                "sequence_id": idx,
                "timeline_date": timestamp_str,
                "metrics": {
                    "raw_cost": f"${cost:,.2f}",
                    "current_z_score": round(z_score, 2)
                },
                "visual_states": {
                    "line_color": primary_color,
                    "alert_glow_alpha": bg_alert_intensity,
                    "text_animation": text_effect,
                    "chart_indicator_radius": int(max(8, abs(z_score) * 6)) # Circle expands dynamically with the math anomaly
                },
                "audio_instructions": {
                    "ducking_profile": narration_cue,
                    "target_voice_pacing": "slow_deliberate" if is_anomaly else "standard"
                },
                "layout": base_layout
            }
            
            scene_events.append(frame_state)
            
        return scene_events