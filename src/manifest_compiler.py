import json
import os
from typing import Dict, Any, List

class ManifestCompiler:
    def __init__(self, output_path: str = "output/manifest.json"):
        self.output_path = output_path
        
    def build_meta(self, total_duration: float) -> Dict[str, Any]:
        """Generates top-level video metadata."""
        return {
            "project": "The Agentic Engineer - Episode 2",
            "resolution": [1920, 1080],
            "fps": 30,
            "total_duration": round(total_duration, 2)
        }

    def build_audio_tracks(self, voiceover_path: str, ducking_profile: str) -> Dict[str, Any]:
        """Maps audio assets and ducking parameters established by the prosody engine."""
        return {
            "voiceover": {
                "source": voiceover_path,
                "ducking_profile": ducking_profile
            },
            "background_music": {
                "source": "assets/audio/ambient_synth.mp3",
                "base_volume": 0.12
            }
        }

    def compile_scene(
        self, 
        scene_id: int, 
        start: float, 
        end: float, 
        bg_source: str,
        layout_spec: Dict[str, Any],
        anomalies: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Assembles a single scene timeline item, explicitly mapping 
        layout_engine_v2 and financial_sentinel variables.
        """
        # Using .get() fallbacks to mirror layout_engine_v2's defensive design
        glitch_config = layout_spec.get("glitch_fx", {})
        
        return {
            "scene_id": scene_id,
            "start_time": round(start, 2),
            "end_time": round(end, 2),
            "visuals": {
                "background": {
                    "type": "video" if bg_source.endswith(".mp4") else "image",
                    "source": bg_source,
                    "loop": True
                },
                "code_overlay": {
                    "type": "syntax_highlighted_text",
                    "source": layout_spec.get("source_file", "main.py"),
                    "position": layout_spec.get("position", ["center", "center"]),
                    "opacity": layout_spec.get("opacity", 0.95)
                }
            },
            "data_overlays": [
                {
                    "overlay_type": "anomaly_alert",
                    "trigger_time": round(anomaly.get("timestamp", start + 1.0), 2),
                    "duration": round(anomaly.get("duration", 3.0), 2),
                    "z_score": round(anomaly.get("z_score", 0.0), 4),
                    "ui_color": layout_spec.get("alert_color", "#FF3333"),
                    "effects": {
                        "glitch_shake": glitch_config.get("coordinate_shake", False),
                        "opacity_pulse": [
                            layout_spec.get("min_opacity", 0.4), 
                            layout_spec.get("max_opacity", 1.0)
                        ]
                    }
                }
                for anomaly in anomalies
            ]
        }

    def export_manifest(self, manifest_data: Dict[str, Any]) -> str:
        """Writes the compiled manifest to disk securely."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        with open(self.output_path, "w") as f:
            json.dump(manifest_data, f, indent=2)
        return self.output_path

# Quick local execution check
if __name__ == "__main__":
    compiler = ManifestCompiler()
    print("Manifest Compiler initialized successfully.")