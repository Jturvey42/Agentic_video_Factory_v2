# src/timeline_compiler.py
import os
import json
import random
import cv2  
import numpy as np  
from moviepy.editor import AudioFileClip, CompositeAudioClip, CompositeVideoClip, VideoFileClip, ColorClip, TextClip
from pathlib import Path

class MoviePyTimelineCompiler:
    def __init__(self, episode_num: int):
        self.episode_num = episode_num
        self.src_dir = os.path.dirname(os.path.abspath(__file__))        
        self.base_dir = os.path.dirname(self.src_dir)                         
        
        manifest_filename = f"video_manifest_ep{self.episode_num}.json"
        self.manifest_path = os.path.join(self.base_dir, manifest_filename)
        self.manifest = self._load_manifest()
        
    def _load_manifest(self) -> dict:
        if not os.path.exists(self.manifest_path):
            raise FileNotFoundError(f"Missing crucial data contract asset: {self.manifest_path}")
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _compile_frames_with_opencv(self, frame_dir: str, output_video_path: str, fps: int) -> str:
        frame_files = [os.path.join(frame_dir, f) for f in sorted(os.listdir(frame_dir)) if f.endswith('.png')]
        if not frame_files:
            raise FileNotFoundError(f"No frames found in {frame_dir}")
            
        first_frame = cv2.imread(frame_files[0])
        height, width, _ = first_frame.shape

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_video_path, fourcc, fps, (width, height))

        print(f"[OPENCV BRIDGE] Compiling {len(frame_files)} telemetry frames...")
        for file in frame_files:
            img = cv2.imread(file)
            writer.write(img)
            
        writer.release()
        print(f"[SUCCESS] OpenCV clip locked down: {output_video_path}")
        return output_video_path

    def build_audio_mix(self):
        project_root = Path(__file__).resolve().parent.parent
        narration_dir = project_root / "audio" / "narration"
        music_dir = project_root / "music"
        staged_clips = []
        current_offset = 0.0  

        try:
            if narration_dir.exists():
                narration_files = sorted(list(narration_dir.glob("ep2_act_*_narration.wav")))
                print("[AUDIO ENGINE] Sequencing narration clips back-to-back...")
                for n_file in narration_files:
                    narr_clip = AudioFileClip(str(n_file))
                    narr_clip = narr_clip.set_start(current_offset)
                    staged_clips.append(narr_clip)
                    current_offset += narr_clip.duration
            else:
                raise FileNotFoundError(f"Critical: Narration directory not found at {narration_dir}")

            if music_dir.exists():
                music_tracks = list(music_dir.glob("*.mp3"))
                if music_tracks:
                    selected_track = random.choice(music_tracks)
                    bg_clip = AudioFileClip(str(selected_track))
                    if bg_clip.duration > current_offset and current_offset > 0:
                        bg_clip = bg_clip.set_duration(current_offset)
                    bg_clip = bg_clip.volumex(0.05).set_start(0.0)
                    staged_clips.append(bg_clip)

            print(f"[SUCCESS] Audio timeline stabilized. Total expected duration: {current_offset:.2f}s")
            return CompositeAudioClip(staged_clips), current_offset
        except Exception as e:
            print(f"[Critical Failure] Audio pipeline processing error: {str(e)}")
            raise e
        
    def build_glitch_position_func(self, base_x: int, base_y: int, intensity: int, start_t: float, end_t: float):
        def shake_transformer(t):
            if start_t <= t <= end_t:
                np.random.seed(int(t * 1000) & 0xFFFFFFFF)
                dx = np.random.randint(-intensity, intensity + 1)
                dy = np.random.randint(-intensity, intensity + 1)
                return (base_x + dx, base_y + dy)
            return (base_x, base_y)
        return shake_transformer
    
    def process_scene_clips(self) -> list:
        print("[VISUAL STAGING] Parsing data contract timeline dynamically via asset runtimes...")
        visual_stack = []
        fps = self.manifest["meta"]["fps"]
        target_resolution = tuple(self.manifest["meta"]["resolution"])

        frame_dir = os.path.join(self.base_dir, "output", "chart_frames")
        temp_chart_video = os.path.join(self.base_dir, "output", f"temp_ep{self.episode_num}_charts.mp4")
        charts_compiled = False
        
        # Chronological tracking variables 
        current_visual_timeline_pointer = 0.0
        chart_video_marker = 0.0
        
        project_root = Path(__file__).resolve().parent.parent
        narration_dir = project_root / "audio" / "narration"

        for clip_data in self.manifest["timeline"]:
            act_num = clip_data["act"]
            
            # ASSET RUNTIME DISCOVERY: Match visual duration strictly to the audio file
            wav_name = f"ep{self.episode_num}_act_{act_num}_narration.wav"
            wav_path = narration_dir / wav_name
            
            if wav_path.exists():
                audio_asset = AudioFileClip(str(wav_path))
                duration = audio_asset.duration
                audio_asset.close() # Free file handle
            else:
                # Safe fallback if audio file isn't found
                duration = float(clip_data["end_time"]) - float(clip_data["start_time"])
                
            start_time = current_visual_timeline_pointer
            end_time = start_time + duration
            
            visual_type = clip_data["visuals"]["background"]["type"]
            source_path = os.path.join(self.base_dir, clip_data["visuals"]["background"]["source"])

            try:
                if visual_type == "video":
                    if os.path.exists(source_path):
                        video_clip = VideoFileClip(source_path)
                        # Loop video background clip if it is shorter than narration track
                        if video_clip.duration < duration:
                            from moviepy.video.fx.loop import loop
                            video_layer = loop(video_clip, duration=duration).resize(target_resolution)
                        else:
                            video_layer = video_clip.subclip(0, duration).resize(target_resolution)
                            
                        video_layer = video_layer.set_start(start_time).set_duration(duration)
                        visual_stack.append(video_layer)
                    else:
                        print(f"[Warning] Asset missing for Act {act_num}: {source_path}")

                elif visual_type == "chart_sequence":
                    if not charts_compiled:
                        self._compile_frames_with_opencv(frame_dir, temp_chart_video, fps)
                        charts_compiled = True

                    if os.path.exists(temp_chart_video):
                        slice_start = chart_video_marker
                        slice_end = chart_video_marker + duration
                        
                        chart_layer = VideoFileClip(temp_chart_video).subclip(slice_start, slice_end).resize(target_resolution)
                        chart_layer = chart_layer.set_start(start_time).set_duration(duration)
                        
                        chart_video_marker += duration
                        
                        # DATA ANOMALY HUD OVERLAY ENGINE
                        if "data_overlays" in clip_data:
                            for overlay in clip_data["data_overlays"]:
                                if overlay.get("overlay_type") == "anomaly_alert":
                                    # Anchor the layout overlay relatively to the dynamic start time
                                    manifest_start = float(clip_data["start_time"])
                                    manifest_trigger = float(overlay["trigger_time"])
                                    relative_delay = manifest_trigger - manifest_start
                                    
                                    trigger = start_time + relative_delay
                                    dur = float(overlay["duration"])
                                    z_val = overlay.get("z_score", 3.12)
                                    
                                    hud_box = (ColorClip(size=(650, 100), color=(255, 17, 17))
                                               .set_opacity(0.85)
                                               .set_start(trigger)
                                               .set_duration(dur)
                                               .set_position(('center', 120)))
                                    
                                    alert_text = (TextClip(f"CRITICAL Z-SCORE OUTLIER: {z_val} !!", 
                                                           fontsize=28, color='white', font='Courier-Bold', size=(650, 100), method='label')
                                                  .set_start(trigger)
                                                  .set_duration(dur)
                                                  .set_position(('center', 120)))
                                    
                                    if overlay["effects"].get("glitch_shake"):
                                        print(f" -> [HUD EFFECT] Activating Z-Score Glitch Shake HUD Overlays at {trigger:.2f}s")
                                        shake_effect = self.build_glitch_position_func(0, 0, intensity=16, start_t=trigger, end_t=trigger+dur)
                                        chart_layer = chart_layer.set_position(shake_effect)
                                        hud_box = hud_box.set_position(self.build_glitch_position_func(635, 120, intensity=16, start_t=trigger, end_t=trigger+dur))
                                        alert_text = alert_text.set_position(self.build_glitch_position_func(635, 120, intensity=16, start_t=trigger, end_t=trigger+dur))
                                    
                                    visual_stack.append(hud_box)
                                    visual_stack.append(alert_text)
                        
                        visual_stack.append(chart_layer)
                    else:
                        raise FileNotFoundError(f"Stitched chart reference missing: {temp_chart_video}")

            except Exception as e:
                print(f"[Critical Failure] Failed staging layer segment for Act {act_num}: {str(e)}")
                raise e

            # Shift tracking clock forward based on the physical size of the asset
            current_visual_timeline_pointer += duration

        if not visual_stack:
            raise RuntimeError("Visual canvas layer array initialization failed.")

        return visual_stack
    
    def execute_master_render(self, output_filename: str):
        audio_mix, total_audio_duration = self.build_audio_mix()
        visual_stack = self.process_scene_clips()
        
        print(f"[RENDER] Finalizing composition layer stacks. Dynamic Video Length: {total_audio_duration:.2f}s")
        
        final_video = CompositeVideoClip(visual_stack, size=tuple(self.manifest["meta"]["resolution"]))
        final_video = final_video.set_audio(audio_mix).set_duration(total_audio_duration)
        
        print(f"[RENDER] Transcoding output stream to {output_filename}...")
        final_video.write_videofile(
            output_filename,
            fps=self.manifest["meta"]["fps"],
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger="bar"
        )
        print("[SUCCESS] Master render file processing complete.")