# src/timeline_compiler.py
import os, json, random, cv2
import numpy as np
from moviepy.editor import (
    AudioFileClip, CompositeAudioClip, CompositeVideoClip, 
    VideoFileClip, ColorClip, ImageClip
)
from pathlib import Path

class MoviePyTimelineCompiler:
    def __init__(self, episode_num: int):
        self.episode_num = episode_num
        self.src_dir = os.path.dirname(os.path.abspath(__file__))        
        self.base_dir = os.path.dirname(self.src_dir)                                         
        self.manifest_path = os.path.join(self.base_dir, f"video_manifest_ep{self.episode_num}.json")
        with open(self.manifest_path, 'r', encoding='utf-8') as f: 
            self.manifest = json.load(f)
        self.is_legacy_schema = "timeline" in self.manifest
        
    def _compile_frames_with_opencv(self, frame_dir: str, output_video_path: str, fps: int) -> str:
        frame_files = [os.path.join(frame_dir, f) for f in sorted(os.listdir(frame_dir)) if f.endswith('.png')]
        first_frame = cv2.imread(frame_files[0])
        height, width, _ = first_frame.shape
        writer = cv2.VideoWriter(output_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
        for file in frame_files: 
            writer.write(cv2.imread(file))
        writer.release()
        return output_video_path

    def build_audio_mix(self):
        project_root = Path(__file__).resolve().parent.parent
        narration_dir = project_root / "audio" / "narration"
        music_dir = project_root / "music"
        staged_clips, current_offset = [], 0.0 
        scenes = self.manifest.get("scenes", [])
        narration_files = [narration_dir / f"ep3_{sc['scene_id']}_narration.wav" for sc in scenes]
        
        for n_file in narration_files:
            if not os.path.exists(n_file):
                continue
            narr_clip = AudioFileClip(str(n_file)).set_start(current_offset)
            staged_clips.append(narr_clip)
            current_offset += narr_clip.duration

        if music_dir.exists():
            music_tracks = list(music_dir.glob("*.mp3"))
            if music_tracks:
                bg_clip = AudioFileClip(str(random.choice(music_tracks)))
                if bg_clip.duration > current_offset and current_offset > 0: 
                    bg_clip = bg_clip.set_duration(current_offset + 2.0)  # Add padding to music loop
                staged_clips.append(bg_clip.volumex(0.05).set_start(0.0))
        return CompositeAudioClip(staged_clips), current_offset

    def process_scene_clips(self) -> tuple:
        visual_stack = []
        meta_block = self.manifest.get("settings", {})
        fps = meta_block["fps"]
        target_resolution = tuple(meta_block["resolution"])
        frame_dir = os.path.join(self.base_dir, "data", "charts_ep3")
        temp_chart_video = os.path.join(self.base_dir, "output", f"temp_ep{self.episode_num}_charts.mp4")
        charts_compiled = False
        current_visual_timeline_pointer, chart_video_marker = 0.0, 0.0
        narration_dir = Path(__file__).resolve().parent.parent / "audio" / "narration"

        for idx, clip_data in enumerate(self.manifest["scenes"]):
            scene_id = clip_data["scene_id"]
            wav_path = narration_dir / f"ep3_{scene_id}_narration.wav"
            
            # Explicitly capture real duration or default
            duration = AudioFileClip(str(wav_path)).duration if wav_path.exists() else 10.0
            start_time = current_visual_timeline_pointer
            
            visual_layers = clip_data.get("visual_layers", {})
            layout_mode = visual_layers.get("layout_mode", "content_focus")
            source_path = os.path.join(self.base_dir, visual_layers.get("background", ""))

            if os.path.exists(source_path) and source_path.endswith('.mp4'):
                video_clip = VideoFileClip(source_path)
                if video_clip.duration < duration:
                    from moviepy.video.fx.loop import loop
                    video_layer = loop(video_clip, duration=duration).resize(target_resolution)
                else: 
                    video_layer = video_clip.subclip(0, duration).resize(target_resolution)
            else: 
                video_layer = ColorClip(size=target_resolution, color=(24, 24, 27)).set_duration(duration)
            
            video_layer = video_layer.set_start(start_time).set_duration(duration)
            visual_stack.append(video_layer)

            hud_image_path = os.path.join(self.base_dir, "data", f"milestone_hud_{scene_id}.png")
            if layout_mode == "checklist_focus":
                if os.path.exists(hud_image_path):
                    visual_stack.append(ImageClip(hud_image_path).set_start(start_time).set_duration(duration).resize(target_resolution).set_position(('center', 'center')))
            else:
                if os.path.exists(frame_dir) and not charts_compiled:
                    self._compile_frames_with_opencv(frame_dir, temp_chart_video, fps)
                    charts_compiled = True
                if os.path.exists(temp_chart_video):
                    slice_start = chart_video_marker
                    slice_end = chart_video_marker + duration
                    with VideoFileClip(temp_chart_video) as ch_vid: 
                        max_ch_dur = ch_vid.duration
                    if slice_end > max_ch_dur: 
                        slice_end = max_ch_dur
                    if slice_end > slice_start:
                        chart_layer = VideoFileClip(temp_chart_video).subclip(slice_start, slice_end).resize((1100, 618)).set_start(start_time).set_duration(slice_end - slice_start).set_position((700, 230))
                        visual_stack.append(chart_layer)
                        chart_video_marker += (slice_end - slice_start)
                if os.path.exists(hud_image_path):
                    visual_stack.append(ImageClip(hud_image_path).set_start(start_time).set_duration(duration).resize(target_resolution).set_position(('center', 'center')))

            current_visual_timeline_pointer += duration
            
        return visual_stack, current_visual_timeline_pointer
   
    def execute_master_render(self, output_filename: str):
        audio_mix, total_audio_duration = self.build_audio_mix()
        visual_stack, total_visual_duration = self.process_scene_clips()
        meta_block = self.manifest["settings"]
        
        # FIX: Align boundaries to the maximum track length + 1.5s clean tail pad
        render_duration = max(total_audio_duration, total_visual_duration) + 1.5
        
        final_video = (CompositeVideoClip(visual_stack, size=tuple(meta_block["resolution"]))
                       .set_audio(audio_mix)
                       .set_duration(render_duration))
                       
        final_video.write_videofile(output_filename, fps=meta_block["fps"], codec="libx264", audio_codec="aac", threads=4, logger="bar")