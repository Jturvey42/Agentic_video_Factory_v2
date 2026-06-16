import os
import sys
# Standard, verified import path for MoviePy v1.0.3
from moviepy.editor import ImageClip, AudioFileClip

# --- CONFIGURATION & PATHS ---
PROJECT_ROOT = "E:/Agentic_Video_Factory_v2"
CHART_PATH = os.path.join(PROJECT_ROOT, "assets/roi_chart.png")
AUDIO_PATH = os.path.join(PROJECT_ROOT, "audio/narration/act_1_narration.wav") 
OUTPUT_VIDEO_PATH = os.path.join(PROJECT_ROOT, "outputs/scene_1.mp4")

def validate_assets():
    """Guardrail: Ensure upstream data blocks are fully present before compilation."""
    if not os.path.exists(CHART_PATH):
        print(f"[ERROR] Step 2 asset missing: {CHART_PATH}")
        sys.exit(1)
    if not os.path.exists(AUDIO_PATH):
        print(f"[ERROR] Step 1 asset missing: {AUDIO_PATH}")
        print("[CRITICAL] Please update AUDIO_PATH if your audio file has a different filename.")
        sys.exit(1)
        
    os.makedirs(os.path.dirname(OUTPUT_VIDEO_PATH), exist_ok=True)

def compose_scene():
    validate_assets()
    
    print("[LOG] Ingesting telemetry audio track...")
    audio_clip = AudioFileClip(AUDIO_PATH)
    duration = audio_clip.duration
    print(f"[LOG] Target sequence length calculated: {duration:.2f} seconds")
    
    print("[LOG] Binding high-contrast static asset to timeline matrix...")
    # Generate image clip set to match the exact runtime of the vocal layer
    video_clip = ImageClip(CHART_PATH).set_duration(duration)
    
    # Merge visual framework with audio track
    final_clip = video_clip.set_audio(audio_clip)
    
    print(f"[LOG] Initiating rendering pipeline target: {OUTPUT_VIDEO_PATH}")
    # Render with standard high-compatibility H.264 video codec and AAC audio encoding
    final_clip.write_videofile(
        OUTPUT_VIDEO_PATH,
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        threads=4,
        logger="bar"
    )
    
    # Explicitly release system handles to avoid venv locks on assets
    audio_clip.close()
    video_clip.close()
    final_clip.close()
    print(f"[SUCCESS] The Agentic Engineer - Episode 1 (Scene 1) successfully generated!")

if __name__ == "__main__":
    compose_scene()