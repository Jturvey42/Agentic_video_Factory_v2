# layout_engine_v2.py
import numpy as np

class TelemetryLayoutEngineV2:
    def __init__(self, canvas_width: int = 1920, canvas_height: int = 1080):
        """
        Upgraded Layout Engine for Episode 2. Consumes telemetry data frames 
        and drives dynamic canvas transformations (glitch shakes, color shifts, auto-scaling shapes).
        """
        self.w = canvas_width
        self.h = canvas_height

    def compute_text_glitch_offset(self, animation_type: str, seed: int) -> tuple:
        """
        Calculates screen vibration coordinate offsets if an active anomaly 
        triggers a text shake effect.
        """
        if animation_type == "shake_heavy":
            np.random.seed(seed)
            # Generate a violent screen vibration offset between -12 and +12 pixels
            dx = int(np.random.randint(-12, 13))
            dy = int(np.random.randint(-12, 13))
            return dx, dy
        return 0, 0

    def generate_frame_render_spec(self, frame_manifest: dict, frame_number: int) -> dict:
        """
        Processes a single second's manifest metadata to establish exact shape dimensions, 
        text strings, and opacity settings for the rendering pipeline.
        """
        layout_config = frame_manifest["layout"]
        chart_box = layout_config["chart_box"]
        visuals = frame_manifest["visual_states"]
        metrics = frame_manifest["metrics"]

        # Calculate text position modifications based on data shake effects
        dx, dy = self.compute_text_glitch_offset(visuals["text_animation"], seed=frame_number)

        render_spec = {
            "frame_id": frame_number,
            "background": {
                "base_color": "#0B0F19", # Deep slate tech background
                "alert_glow_color": "#FF0000",
                "alert_opacity": visuals["alert_glow_alpha"] # Glow intensity scales with Z-Score severity
            },
            "chart_ui": {
                "bounding_box": chart_box,
                "line_color": visuals["line_color"],
                "target_node": {
                    "radius": visuals["chart_indicator_radius"], # Dot expands dynamically with the anomaly math
                    "color": visuals["line_color"]
                }
            },
            "typography": {
                "date_label": {
                    "text": f"TIMELINE: {frame_manifest['timeline_date']}",
                    "x": 200 + dx,
                    "y": 150 + dy,
                    "color": "#FFFFFF",
                    "font_size": 32
                },
                "cost_readout": {
                    "text": f"DAILY INFRA SPEND: {metrics['raw_cost']}",
                    "x": 200 + dx,
                    "y": 880 + dy,
                    "color": visuals["line_color"], # Text changes color alongside the chart line
                    "font_size": 48
                },
                "z_score_readout": {
                    "text": f"METRIC DEVIATION [Z]: {metrics['current_z_score']}",
                    "x": 200 + dx,
                    "y": 950 + dy,
                    "color": "#8A99AD" if not frame_manifest.get("is_anomaly", False) else "#FF3333",
                    "font_size": 28
                }
            },
            "audio_mixing": frame_manifest["audio_instructions"]
        }

        return render_spec