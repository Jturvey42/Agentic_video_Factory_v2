# E:/Agentic_Video_Factory_v2/layout_engine.py
import os
from moviepy.editor import ImageClip, TextClip, CompositeVideoClip, AudioFileClip, ColorClip

def create_scene_clip(act_data: dict, audio_path: str, fast_preview: bool = False):
    """
    Composes a stable 1920x1080 split-screen layout.
    Left Side: Code/Visual Asset scaled proportionally inside a windowed slate background.
    Right Side: Solid slate card background with constrained, readable explanation text.
    """
    audio = AudioFileClip(audio_path)
    
    # Fast Preview Optimization: Capping clip duration down for testing loops
    duration = min(3.0, audio.duration) if fast_preview else audio.duration
    
    canvas_w, canvas_h = 1920, 1080
    half_width = canvas_w // 2  # 960px
    
    visual_layers = []
    
    # --- 1. LEFT SCREEN: CODE / ARTIFACT (WINDOWED) ---
    left_image_path = f"E:/Agentic_Video_Factory_v2/temp/act_{act_data['act']}_left.png"
    if os.path.exists(left_image_path):
        # Create a dedicated deep gray terminal background for the left half
        left_panel_bg = (ColorClip(size=(half_width, canvas_h), color=(30, 32, 36))
                         .set_duration(duration)
                         .set_position((0, 0)))
        visual_layers.append(left_panel_bg)
        
        # Add 40px internal margin padding so text doesn't touch edges
        padding = 40
        allowed_w = half_width - (padding * 2)  # 880px available width
        
        # Load the code screenshot and scale its width proportionally
        code_clip = (ImageClip(left_image_path)
                     .set_duration(duration)
                     .resize(width=allowed_w))
        
        # Center the code clip vertically inside the left panel block
        code_y = (canvas_h - code_clip.h) // 2
        code_clip = code_clip.set_position((padding, code_y))
        
        visual_layers.append(code_clip)
    else:
        # Fallback dark gray panel if asset generation failed
        left_placeholder = (ColorClip(size=(half_width, canvas_h), color=(25, 25, 25))
                            .set_duration(duration)
                            .set_position((0, 0)))
        visual_layers.append(left_placeholder)
        
   # --- 2. RIGHT SCREEN: TEXT CARD BACKGROUND / IMAGE VISUAL ---
    right_visual_cfg = act_data.get("visuals", {}).get("right_screen", {})
    right_image_path = right_visual_cfg.get("source_path", "")

    # Check if an image asset is specified and exists on disk
    if right_image_path and os.path.exists(right_image_path):
        right_bg = (ImageClip(right_image_path)
                    .set_duration(duration)
                    .resize(newsize=(half_width, canvas_h)) # Snap to exactly 960x1080
                    .set_position((half_width, 0)))
    else:
        # Fallback to the original solid slate card background if no image exists
        right_bg = (ColorClip(size=(half_width, canvas_h), color=(20, 22, 26))
                    .set_duration(duration)
                    .set_position((half_width, 0)))
                    
    visual_layers.append(right_bg)

    # --- 3. CONSTRAINED NARRATION TEXT (RIGHT SIDE ONLY) ---
    text_padding = 60
    caption_w = half_width - (text_padding * 2)  # 840px wide maximum bounding box
    caption_h = 600                             # Generous layout vertical tracking box
    
    caption = (TextClip(
        txt=act_data["narration_text"],  
        fontsize=32,          
        color='yellow', 
        font=r'C:\Windows\Fonts\arial.ttf',
        method='caption',
        size=(caption_w, caption_h),
        align='West'  # Left-aligned body formatting for clean code-blog aesthetic
    )
    .set_duration(duration)
    .set_position((half_width + text_padding, (canvas_h - caption_h) // 2))) 
    
    visual_layers.append(caption)
    
    # --- FINAL TIMELINE COMPOSITION ---
    final_scene = CompositeVideoClip(visual_layers, size=(canvas_w, canvas_h))
    
    if fast_preview:
        final_scene = final_scene.set_audio(audio.subclip(0, duration))
    else:
        final_scene = final_scene.set_audio(audio)
                       
    return final_scene