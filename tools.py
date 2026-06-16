import os
import soundfile as sf
from dataclasses import dataclass
from kokoro_onnx import Kokoro
from moviepy.editor import ImageClip, AudioFileClip, CompositeAudioClip
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter

@dataclass
class SceneData:
    id: int
    narration: str
    code_snippet: str
    visual_asset: str = "" 

def generate_scene_audio(act_id: int, narration_text: str) -> str:
    """Generates the speech wav asset from narration text using Kokoro ONNX."""
    print(f"--- [Audio] Generating Act {act_id} ---")
    base_path = "E:/Agentic_Video_Factory_v2"
    model_file = f"{base_path}/kokoro.onnx"
    voices_file = f"{base_path}/voices-v1.0.bin"
    
    # --- SANITIZE STRING TO ELIMINATE UNNATURAL TTS PAUSES ---
    # 1. Replace line breaks and carriage returns with standard spaces
    clean_text = narration_text.replace("\n", " ").replace("\r", " ")
    
    # 2. Clean out any double or triple spacing artifacts created by the stripping process
    while "  " in clean_text:
        clean_text = clean_text.replace("  ", " ")
        
    # 3. Strip trailing white space from the boundaries of the string
    clean_text = clean_text.strip()
    
    # Swap the original variable with our pristine, flattened string
    narration_text = clean_text
    # ---------------------------------------------------------

    if not os.path.exists(model_file) or not os.path.exists(voices_file):
        raise FileNotFoundError(f"Missing Kokoro files at {base_path}. Please check your E: drive.")

    kokoro = Kokoro(model_file, voices_file) 
    audio_path = f"E:/Agentic_Video_Factory_v2/assets/audio/scene_{act_id}.wav"
    os.makedirs(os.path.dirname(audio_path), exist_ok=True)
    
    samples, sample_rate = kokoro.create(
        narration_text, 
        voice="am_michael", 
        speed=1.0, 
        lang="en-us"
    )
    
    sf.write(audio_path, samples, sample_rate)
    return audio_path

def generate_code_image(act_id: int, left_screen_config: dict) -> str:
    """
    Reads a specific line range from a source code file based on the manifest,
    highlights it via Pygments, and saves it as a 960px-wide side-panel PNG.
    """
    print(f"--- [Image] Extracting & Highlighting Code for Act {act_id} ---")
    output_path = f"E:/Agentic_Video_Factory_v2/temp/act_{act_id}_left.png"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    source_file = left_screen_config.get("source_file")
    start_line = left_screen_config.get("start_line", 1)
    end_line = left_screen_config.get("end_line", 20)

    # 1. Extract specified line block safely
    if not source_file or not os.path.exists(source_file):
        # Fallback snippet if the source file target isn't created yet
        code_block = f"# Source code file missing:\n# {source_file}\n# Act {act_id} Fallback code block."
    else:
        with open(source_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Extract slices cleanly (accounting for 0-indexed lists vs 1-indexed line numbers)
        selected_lines = lines[start_line - 1 : end_line]
        code_block = "".join(selected_lines)

    # 2. Setup standard dark-mode code formatting
    formatter = ImageFormatter(
        style='monokai', 
        font_size=24, 
        line_numbers=True, 
        line_number_start=start_line,
        padding=40
    )
    
    with open(output_path, "wb") as f:
        f.write(highlight(code_block, PythonLexer(), formatter))
    
    return output_path

def apply_background_music(video_clip, music_path, volume=0.15):
    """Applies background track using strictly legacy MoviePy v1.0.3 loop syntax."""
    bg_music = AudioFileClip(music_path)
    
    # Ensure background loop starts cleanly at the beginning
    bg_music = bg_music.set_start(0) 
    
    # In MoviePy 1.0.3, fx.all.audio_loop can loop directly to match a given duration
    if bg_music.duration < video_clip.duration:
        from moviepy.audio.fx.all import audio_loop
        # Legacy v1.0.3 accepts the clip, and optionally an explicit duration target
        bg_music = audio_loop(bg_music, duration=video_clip.duration)
    else:
        bg_music = bg_music.set_duration(video_clip.duration)
        
    bg_music = bg_music.volumex(volume)
    
    if video_clip.audio:
        narration = video_clip.audio.set_start(0)
        # Combine using standard v1.0.3 composition array rules
        new_audio = CompositeAudioClip([narration, bg_music])
        return video_clip.set_audio(new_audio) 
    
    return video_clip.set_audio(bg_music)