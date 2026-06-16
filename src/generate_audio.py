# src/generate_audio.py
import json
import os
import soundfile as sf
from kokoro_onnx import Kokoro  # Local Kokoro-ONNX setup

def build_voiceover_tracks(episode_num: int):
    """
    Dynamically tracks repository paths relatively and generates audio stems
    prefixed by the designated episode number to prevent collisions.
    """
    # 1. DYNAMIC PATHING: Calculate project root relative to this file's location
    src_dir = os.path.dirname(os.path.abspath(__file__))          # E:/.../src/
    base_dir = os.path.dirname(src_dir)                           # E:/Agentic_Video_Factory_v2/
    
    # 2. Define dynamic targets based on the Episode variable
    manifest_filename = f"video_manifest_ep{episode_num}.json"
    manifest_path = os.path.join(base_dir, manifest_filename)
    output_dir = os.path.join(base_dir, "audio", "narration")
    
    # Verify the target manifest contract exists before running heavy models
    if not os.path.exists(manifest_path):
        raise FileNotFoundError(f"[ERROR] Strict data contract missing for execution: {manifest_path}")
        
    # 3. Load the specific video manifest configuration
    with open(manifest_path, 'r') as f:
        config = json.load(f)
    
    # 4. Initialize local Kokoro model dynamically from base project directory
    model_path = os.path.join(base_dir, "kokoro.onnx")
    voices_path = os.path.join(base_dir, "voices-v1.0.bin")
    
    kokoro = Kokoro(model_path, voices_path)
    print(f"Executing Audio Generation pipeline for: {config['project_name']}\n---")
    
    # Ensure the dynamic output folder path exists safely on the host machine
    os.makedirs(output_dir, exist_ok=True)
    
    # 5. Step through each act sequentially
    for scene in config['timeline']:
        act_num = scene['act']
        text = scene['narration_text']
        
        # DYNAMIC FILENAME: Prefixed cleanly by episode number
        filename = f"ep{episode_num}_act_{act_num}_narration.wav"
        output_path = os.path.join(output_dir, filename)
        
        print(f" -> Synthesizing Track: {filename}...")
        
        # Create audio stream using the 'michael' voice profile
        samples, sample_rate = kokoro.create(text, voice="am_michael", speed=1.0)
        
        # Save raw audio file down to the calculated relative directory
        sf.write(output_path, samples, sample_rate)
        print(f"[SUCCESS] Stem locked down: {output_path}")

if __name__ == "__main__":
    # CONTROL PANEL: Change this single integer to instantly shift the pipeline execution target
    EPISODE_NUM = 2 
    
    build_voiceover_tracks(episode_num=EPISODE_NUM)