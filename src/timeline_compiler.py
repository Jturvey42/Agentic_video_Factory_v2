# src/timeline_compiler.py
import os
import glob
import json
import random
import cv2
import sys
import numpy as np
from moviepy.editor import (
    ImageSequenceClip,
    AudioFileClip, CompositeAudioClip, CompositeVideoClip, 
    VideoFileClip, ColorClip, ImageClip, TextClip
)
from pathlib import Path

class MoviePyTimelineCompiler:
    def __init__(self, episode_num: int):
        self.episode_num = episode_num
        self.src_dir = os.path.dirname(os.path.abspath(__file__))        
        self.base_dir = os.path.dirname(self.src_dir)
        self.manifest_path = os.path.join(self.base_dir, "video_manifest_ep3_test.json")
        # self.manifest_path = os.path.join(self.base_dir, f"video_manifest_ep{self.episode_num}.json")
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

    def process_scene_clips(self, scene_data, headline_text, is_final_scene=False, audio_tail_pad_seconds=1.5):
        """
        Stitches scene assets into a dynamic layout. Protects against short audio
        tracks by dynamically scaling the layout states to prevent negative durations.
        """
        # 1. Asset Verification & Audio Initialization
        audio_path = scene_data['audio_path']
        if not os.path.exists(audio_path):
            print(f"[-] ERROR: Audio asset missing at {audio_path}")
            sys.exit(1)
            
        audio_clip = AudioFileClip(audio_path)
        base_duration = audio_clip.duration
        
        # Calculate complete scene duration
        total_duration = base_duration + audio_tail_pad_seconds if is_final_scene else base_duration

        # Safeguard: Ensure the scene is long enough to show both stages. Min floor = 8.0s
        if total_duration < 8.0:
            total_duration = 8.0

        # 2. Dynamic Base Canvas Generation
        bg_clip = ColorClip(size=(1920, 1080), color=(26, 26, 26)).set_duration(total_duration)

        # 3. State A: Introductory Checklist Layout Initialization
        # Explicitly define intro_duration first to prevent 'NameError'
        intro_duration = 6.0
        
        hud_path = scene_data['hud_overlay_path']
        hud_intro = ImageClip(hud_path) \
            .set_duration(intro_duration) \
            .resize(width=1600) \
            .set_position(('center', 'center'))
        
        # 4. Data Stage State Timeline Setup
        data_stage_start = intro_duration
        data_stage_duration = total_duration - data_stage_start
        
        # 5. Top Headline Configuration (Pushed upward to clear chart space)
        headline_clip = TextClip(
            headline_text, 
            fontsize=40, 
            color='white', 
            font='Arial-Bold',
            size=(1920, 100)
        ).set_start(data_stage_start).set_duration(data_stage_duration).set_position(('center', 30))

        # 6. State B: Center Video/Chart Layer Sequence Handling
        # Re-centered and scaled proportionally by height to protect Y-axis labels
        chart_path = scene_data['chart_sequence_path']
        if os.path.exists(chart_path):
            frame_files = [os.path.join(chart_path, f) for f in sorted(os.listdir(chart_path)) if f.endswith('.png')]
            
            if not frame_files:
                chart_sequence = None
            else:
                chart_sequence = ImageSequenceClip(frame_files, fps=30) \
                    .set_start(data_stage_start) \
                    .set_duration(data_stage_duration) \
                    .resize(height=800) \
                    .set_position(('center', 180))
        else:
            chart_sequence = None

        # 7. Composite Stack Assembly
        clip_stack = [bg_clip, headline_clip]
        if chart_sequence:
            clip_stack.append(chart_sequence)
        clip_stack.append(hud_intro)

        final_clip = CompositeVideoClip(clip_stack, size=(1920, 1080)).set_duration(total_duration)
        return final_clip

    def execute_master_render(self, output_filename: str):
        """
        Stitches all visual scenes together sequentially using concatenate_videoclips
        and pairs them perfectly with the master audio mix.
        """
        from moviepy.editor import concatenate_videoclips
        
        scenes = self.manifest.get("scenes", [])
        total_scenes = len(scenes)
        meta_block = self.manifest["settings"]
        
        processed_video_scenes = []
        
        # 1. Compile all individual visual scene clips
        for idx, scene_data in enumerate(scenes):
            is_final = (idx + 1 == total_scenes)
            headline_text = scene_data.get("headline_text", "Data Telemetry Feed")
            
            scene_clip = self.process_scene_clips(
                scene_data=scene_data, 
                headline_text=headline_text, 
                is_final_scene=is_final
            )
            processed_video_scenes.append(scene_clip)
            
        # 2. Concatenate ALL compiled visual scenes into one unified backbone timeline
        full_visual_timeline = concatenate_videoclips(processed_video_scenes, method="compose")
        video_duration = full_visual_timeline.duration
        
        # 3. Build and lock down the audio mix timeline
        audio_mix, total_audio_duration = self.build_audio_mix()
        audio_mix = audio_mix.set_duration(total_audio_duration)
        
        # 4. Final Padding Verification: Sync video container explicitly to master audio lengths
        if total_audio_duration > video_duration:
            padding_needed = total_audio_duration - video_duration
            tail_padding = ColorClip(size=(1920, 1080), color=(26, 26, 26)) \
                .set_start(video_duration) \
                .set_duration(padding_needed)
            final_video = CompositeVideoClip([full_visual_timeline, tail_padding]).set_duration(total_audio_duration)
        else:
            final_video = full_visual_timeline.set_duration(video_duration)

        # 5. Fuse the final audio mix down to the compiled timeline
        final_video = final_video.set_audio(audio_mix)
        
        # 6. Execute Multi-Threaded Production Render
        final_video.write_videofile(
            output_filename, 
            fps=meta_block["fps"], 
            codec="libx264", 
            audio_codec="aac", 
            threads=4, 
            logger="bar"
        )