import os
import json
import random

# --- PILLOW VERSION COMPATIBILITY PATCH FOR MOVIEPY v1.0.3 ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
# -------------------------------------------------------------

from moviepy.editor import VideoFileClip, concatenate_videoclips
# Map your ImageMagick custom E-drive binary location
os.environ["IMAGEMAGICK_BINARY"] = r"E:\Programs\ImageMagick-7.1.2-Q16-HDRI\convert.exe"

# Import our rebuilt helper tools and layout engine
from tools import generate_scene_audio, generate_code_image, apply_background_music
from layout_engine import create_scene_clip

def assemble_factory_video(manifest_path):
    print(f"=== Starting Build Pipeline for 'The Agentic Engineer' ===")
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
        
    global_settings = manifest["global_settings"]
    act_clips = []
    
    # --- DYNAMIC RANDOM AUDIO TRACK SELECTION ---
    music_dir = r"E:/Agentic_Video_Factory_v2/music"
    # Filter out only valid mp3 files present in the directory
    available_tracks = [f for f in os.listdir(music_dir) if f.endswith('.mp3')]
    
    if available_tracks:
        chosen_track = random.choice(available_tracks)
        bgm_path = os.path.join(music_dir, chosen_track).replace("\\", "/")
        print(f"--- [BGM] Dynamically Selected Track: {chosen_track} ---")
    else:
        # Emergency fallback if the music directory happens to be empty
        bgm_path = global_settings["background_audio"]
        print(f"--- [BGM Warning] No tracks found in {music_dir}. Using manifest setting. ---")
    # --------------------------------------------
    
    # Iterate dynamically through each act in the timeline
    for act_data in manifest["timeline"]:
        act_id = act_data["act"]
        print(f"\n>>> Processing Act {act_id}: {act_data['title']} <<<")
        
        # Step A: Build dynamic audio asset via Kokoro
        audio_path = generate_scene_audio(act_id, act_data["narration_text"])
        
        # Step B: Extract code panel slice via Pygments (Left Screen)
        generate_code_image(act_id, act_data["visuals"]["left_screen"])
        
        # Step C: Compose full 1920x1080 scene layout with text framing fixes
        scene_clip = create_scene_clip(act_data, audio_path)
        act_clips.append(scene_clip)
        
    print(f"\n--- Stitching all {len(act_clips)} acts together ---")
    final_video = concatenate_videoclips(act_clips, method="compose")
    
# Step D: Apply the randomized background music loop safely with Dynamic Audio Ducking
    bgm_volume = global_settings["background_audio_volume"]
    
    # Store a pristine reference of the composite scene audio BEFORE we attach background music
    voice_layer = final_video.audio

    def duck_audio_modifier(get_volume_at_time, current_time):
        """
        Telemetry loop: Senses voice activity on the independent voice_layer reference 
        and ducks the background music down by 80% to maximize narration legibility.
        """
        if voice_layer:
            try:
                # Inspect the isolated voice layer frame instead of the final composition
                voice_frame = voice_layer.get_frame(current_time)
                # Check if there is active amplitude/audio wave signal
                if any(v != 0 for v in voice_frame):
                    return get_volume_at_time(current_time) * 0.20  # Ducked music volume
            except Exception:
                pass
        return get_volume_at_time(current_time)  # Standard background music volume

    # Apply the ducking logic to the background music loop independently
    final_video = apply_background_music(final_video, bgm_path, volume=bgm_volume)
    if final_video.audio:
        # Update the composite audio timeline using our safe modifier function
        final_video.audio = final_video.audio.fl(duck_audio_modifier)
    
# Step E: Render output file
    output_file = global_settings["output_path"]
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # --- DEVELOPMENT OVERRIDE SWITCH ---
    # Set to True for lightning-fast layout testing (seconds). Set to False for production master renders.
    DEV_MODE = True 
    
    if DEV_MODE:
        # Generate a distinct preview path so you can compare iterations easily
        preview_file = os.path.join(os.path.dirname(output_file), "dev_preview.mp4")
        print(f"⚡ --- Commencing Fast Dev Render: {preview_file} --- ⚡")
        
        # Take a 5-second slice of the final video timeline to verify layouts instantly
        final_video.subclip(0, min(5, final_video.duration)).write_videofile(
            preview_file,
            fps=8,                  # Drop frames heavily to reduce processing math
            codec="libx264",
            audio=False,            # Skip slow audio rendering entirely for rapid layout checks
            preset="ultrafast",     # Forces FFmpeg to encode instantly at the expense of compression efficiency
            bitrate="600k"          # Low data rate for immediate disk-write times
        )
        print(f"⚡ === Preview Compiled Successfully in Seconds! Check: {preview_file} ===")
        
    else:
        # Standard Production Master Render
        print(f"--- Commencing Final Master Render: {output_file} ---")
        final_video.write_videofile(
            output_file,
            fps=global_settings["fps"],
            codec="libx264",
            audio_codec="aac"
        )
        print(f"=== Pipeline Run Successful! Production Video Compiled ===")

if __name__ == "__main__":
    assemble_factory_video("E:/Agentic_Video_Factory_v2/video_manifest.json")