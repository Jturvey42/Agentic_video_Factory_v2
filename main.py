import os
os.environ["IMAGEMAGICK_BINARY"] = r"E:\Programs\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
from moviepy import ImageClip, AudioFileClip, ColorClip, CompositeVideoClip, TextClip
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import ImageFormatter
import tools
import random


# --- CONFIGURATION ---
VIDEO_RES = (1920, 1080)
CODE_WIDTH = 1200  # Left side width
TERM_WIDTH = 720   # Right side width
BG_COLOR = (15, 15, 15) # Dark gray/black

def generate_code_ribbon(file_path, output_path):
    """Turns your .py file into a high-res image ribbon."""
    with open(file_path, 'r') as f:
        code = f.read()
    
    # Using Monokai theme for that technical 'Agnostic Engine' look
    formatter = ImageFormatter(
        font_size=24, 
        line_numbers=True, 
        theme='monokai',
        font_name='Consolas' # Common clean mono font
    )
    
    with open(output_path, 'wb') as f:
        f.write(highlight(code, PythonLexer(), formatter))
    return output_path


def create_factory_video(code_img, audio_path, output_path):
    """Composes the scroll and the terminal HUD."""
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # 1. Background
    bg = ColorClip(size=VIDEO_RES, color=BG_COLOR).with_duration(duration)
    
    # 2. Code Scroll Layer
    code_clip = ImageClip(code_img)
    scroll_distance = code_clip.h - VIDEO_RES[1]
    
    # Math: Move from y=0 to y=-scroll_distance over the audio duration
    scrolling_logic = lambda t: (0, - (scroll_distance / duration) * t)
    code_layer = code_clip.with_position(scrolling_logic).with_duration(duration)

    # 3. Terminal HUD Layer (Live Output Simulation)
    terminal_bg = ColorClip(size=(TERM_WIDTH, VIDEO_RES[1]), color=(30, 30, 30))
    terminal_bg = terminal_bg.with_opacity(0.7).with_position((CODE_WIDTH, 0)).with_duration(duration)
    
    status_text = TextClip(
        text="STATUS: AGENTIC ENGINE ACTIVE...\nPROCESING SPY_DATA_POC...", 
        font_size=30,           
        color='green', 
        font=r"C:\Windows\Fonts\consola.ttf"
    ).with_position((CODE_WIDTH + 50, 50)).with_duration(duration)

    # 4. Final Composition
    final = CompositeVideoClip([bg, code_layer, terminal_bg, status_text])
    final = final.with_audio(audio)

    # --- NEW RANDOM MUSIC LOGIC ---
    music_dir = "E:/Agentic_Video_Factory_v2/music"
    if os.path.exists(music_dir):
        # Get list of .mp3 files
        music_files = [f for f in os.listdir(music_dir) if f.endswith('.mp3')]
        
        if music_files:
            random_track = random.choice(music_files)
            music_path = os.path.join(music_dir, random_track)
            
            print(f"--- [Audio] Applying Random Track: {random_track} ---")
            # Apply using tools module and re-assigning to 'final'
            final = tools.apply_background_music(final, music_path, volume=0.12)
        else:
            print(f"Warning: No .mp3 files found in {music_dir}")
    else:
        print(f"Warning: Music directory not found at {music_dir}")
    # ------------------------------
    
    final.write_videofile(output_path, fps=30, codec="libx264", audio_codec="aac")

if __name__ == "__main__":
    # Ensure folders exist
    os.makedirs("inputs", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    # Define Paths
    CODE_IN = "inputs/script.py"       # Put your python code here
    AUDIO_IN = "inputs/narration.wav" # Put your audio here
    VIDEO_OUT = "outputs/agentic_v2_debut.mp4"
    TEMP_IMG = "inputs/temp_ribbon.png"

    if os.path.exists(CODE_IN) and os.path.exists(AUDIO_IN):
        print("--- Starting Agentic Factory Pipeline ---")
        generate_code_ribbon(CODE_IN, TEMP_IMG)
        create_factory_video(TEMP_IMG, AUDIO_IN, VIDEO_OUT)
        print(f"--- Production Complete: {VIDEO_OUT} ---")
    else:
        print(f"Error: Missing files!")
        print(f"Looking for Code: {os.path.exists(CODE_IN)} ({CODE_IN})")
        print(f"Looking for Audio: {os.path.exists(AUDIO_IN)} ({AUDIO_IN})")