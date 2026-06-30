import os
import json
from PIL import Image, ImageDraw, ImageFont

def get_monospace_font(font_size=24):
    """
    Attempts to load common monospace fonts for a clean terminal look,
    falling back safely to the default system font if unavailable.
    """
    font_names = [
        "JetBrainsMono-Bold.ttf", "JetBrainsMono-Regular.ttf",
        "FiraCode-Bold.ttf", "FiraCode-Regular.ttf",
        "Courier New Bold.ttf", "Courier New.ttf", "courbd.ttf"
    ]
    
    for font in font_names:
        try:
            # Check common OS font directories or local path
            return ImageFont.truetype(font, font_size)
        except IOError:
            continue
            
    print("⚠️ Target monospace fonts not found. Falling back to default PIL font.")
    return ImageFont.load_default()

def draw_hud_box(draw, x, y, width, height, title, font, color=(0, 229, 255, 255)):
    """
    Draws a sharp, terminal-style geometric panel box with a corner accent.
    """
    # Outer bounding frame
    draw.rectangle([x, y, x + width, y + height], outline=color, width=2)
    
    # Header tag accent
    tag_w, tag_h = draw.textbbox((0, 0), f"  {title}  ", font=font)[2:4]
    draw.rectangle([x + 10, y - 10, x + 10 + tag_w, y + 5], fill=(24, 24, 27, 255))
    draw.text((x + 10, y - 10), f"  {title}  ", font=font, fill=color)

def generate_polished_hud(manifest_path, output_path):
    """
    Reads the active video manifest and generates a high-production-value 
    terminal UI tracking dashboard asset with dynamic flow highlighting.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 1. Load active data contract
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
        
    episode_title = manifest.get("metadata", {}).get("title", "AGENTIC ENGINE PIPELINE")
    milestones = manifest.get("milestones", [])
    
    # 2. Setup Matte Charcoal Canvas
    canvas_w, canvas_h = 1920, 1080
    image = Image.new("RGBA", (canvas_w, canvas_h), (24, 24, 27, 255)) 
    draw = ImageDraw.Draw(image)
    
    # 3. Initialize Fonts
    font_header = get_monospace_font(font_size=36)
    font_body = get_monospace_font(font_size=26)
    font_status = get_monospace_font(font_size=20)
    
    # 4. Draw Main Dashboard Framing Panel
    hud_x, hud_y = 100, 100
    hud_w, hud_h = 850, 600
    draw_hud_box(draw, hud_x, hud_y, hud_w, hud_h, "SYSTEM GOAL MONITOR", font_status)
    
    # Title Text & Divider
    draw.text((hud_x + 40, hud_y + 40), f">> {episode_title.upper()}", font=font_header, fill=(255, 255, 255, 255))
    draw.line([hud_x + 40, hud_y + 100, hud_x + hud_w - 40, hud_y + 100], fill=(63, 63, 70, 255), width=1)
    
    # 5. Dynamic Milestone Render Loop
    start_y = hud_y + 140
    line_spacing = 75
    
    for idx, milestone in enumerate(milestones):
        # --- DYNAMIC FORMATTING PASS ---
        current_y = start_y + (idx * line_spacing)
        status = milestone.get("status", "pending").lower()
        name = milestone.get("name", f"Milestone {idx + 1}")
        
        if status == "completed":
            status_symbol = "[+]"
            text_color = (0, 200, 100, 180)    # Subdued Emerald (Muted Opacity)
            x_offset = 0                        # Standard alignment
            display_text = f"{status_symbol} {name.upper()}"
            
        elif status == "active":
            status_symbol = ">>"
            text_color = (0, 229, 255, 255)    # Full Electric Cyan
            x_offset = 25                       # Indent to show active execution flow
            display_text = f"{status_symbol} {name.upper()}"
            
            # Draw a subtle background highlight bar for the active process flow
            draw.rectangle(
                [hud_x + 30, current_y - 8, hud_x + hud_w - 30, current_y + 36], 
                fill=(0, 229, 255, 20),          # Ultra-faint cyan tint
                outline=(0, 229, 255, 50),       # Muted border glow
                width=1
            )
            
            # Active status trailing terminal block cursor
            text_w = draw.textbbox((0, 0), display_text, font=font_body)[2]
            draw.rectangle(
                [hud_x + 40 + x_offset + text_w + 10, current_y + 4, hud_x + 40 + x_offset + text_w + 22, current_y + 24], 
                fill=(0, 229, 255, 255)
            )
            
        else: # Pending
            status_symbol = "[ ]"
            text_color = (100, 116, 139, 255)  # Slate Gray
            x_offset = 0                        # Standard alignment
            display_text = f"{status_symbol} {name.upper()}"

        # Render the final styled text line with its dynamic offset
        draw.text(
            (hud_x + 40 + x_offset, current_y), 
            display_text, 
            font=font_body, 
            fill=text_color
        )
            
    image.save(output_path, "PNG")
    print(f"🚀 Success! Polished terminal HUD exported directly to: {output_path}")

if __name__ == "__main__":
    # Test execution path mapped precisely to your active schema structures
    MANIFEST = "video_manifest_ep3.json"
    OUTPUT = "data/milestone_hud.png"
    
    generate_polished_hud(MANIFEST, OUTPUT)