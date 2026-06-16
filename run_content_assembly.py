# run_content_assembly.py
import os
import sys
import json
import shutil
import numpy as np
import pandas as pd

# ==============================================================================
# HARDENED WINDOWS SUBPROCESS PATCH: Class-Level Destructor Protection
# ==============================================================================
if sys.platform == "win32":
    import subprocess

    # 1. Capture the native class-level destructor
    _orig_del = subprocess.Popen.__del__

    def _exception_safe_del(self):
        try:
            # Try running the standard Python cleanup process
            if _orig_del is not None:
                _orig_del(self)
        except OSError as e:
            # If Windows handle recycling races garbage collection, bypass cleanly
            if getattr(e, 'winerror', None) in (5, 6):
                pass
            else:
                raise
        except AttributeError:
            # Handles edge cases where sys or other modules are already None during teardown
            pass

    # 2. Bind directly to the class definition to survive script teardown
    subprocess.Popen.__del__ = _exception_safe_del
# ==============================================================================

# Now safe to import pipeline components that spawn FFMPEG workers
from src.timeline_compiler import MoviePyTimelineCompiler
from src.chart_overlay_engine import TelemetryChartEngine

def main():
    # --------------------------------------------------------------------------
    # CONFIGURATION CONTROL PANEL
    # --------------------------------------------------------------------------
    # Change EPISODE_NUM to instantly target alternate manifests or scripts
    EPISODE_NUM = 2
    
    # Chart generation constants
    TOTAL_CHART_STEPS = 30       # Matching chronological steps for data timeline
    ANOMALY_INDEX = 23          # Index location where the Z-score anomaly spikes
    
    print(f"=== STARTING PHASE 3: EPISODE {EPISODE_NUM} CONTENT ASSEMBLY INTEGRATION ===")
    
    # 1. DYNAMIC PATHING: Calculate project root location relatively
    base_dir = os.path.dirname(os.path.abspath(__file__))
    manifest_filename = f"video_manifest_ep{EPISODE_NUM}.json"
    manifest_path = os.path.join(base_dir, manifest_filename)
    
    # Verify Manifest Data Contract Exists before spinning up models
    if not os.path.exists(manifest_path):
        print(f"[ERROR] Strict data contract missing: {manifest_path}")
        print("Please ensure your manifest JSON file is constructed in the root folder.")
        sys.exit(1)
        
    print(f"[INFO] Verified data contract manifest at: {manifest_path}")

    # ==============================================================================
    # PHASE 1: AUTOMATED NARRATION BUILDER & ASSET ALIGNMENT
    # ==============================================================================
    print("\n=== GENERATING SANITIZED NARRATION AUDIO TRACKS ===")
    try:
        from tools import generate_scene_audio  
        
        # Load the manifest data layout explicitly
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)
            
        narration_output_dir = os.path.join(base_dir, "audio", "narration")
        os.makedirs(narration_output_dir, exist_ok=True)
        
        # Wipe old cached files to ensure a clean overwrite
        print("[INFO] Clearing stale audio cache...")
        for file_name in os.listdir(narration_output_dir):
            if file_name.endswith('.wav'):
                try: 
                    os.remove(os.path.join(narration_output_dir, file_name))
                except Exception: 
                    pass
        
        # Loop through acts and feed matching text parameters to Kokoro
        for item in manifest_data["timeline"]:
            act = item["act"]
            text = item["narration_text"]
            wav_name = f"ep2_act_{act}_narration.wav"
            wav_path = os.path.join(narration_output_dir, wav_name)
            
            print(f" -> Processing Act {act} audio pipeline...")
            
            # CRITICAL FIX: Aligning variables directly to the function signature
            # generate_scene_audio expects: (act_id: int, narration_text: str)
            temp_generated_path = generate_scene_audio(act_id=int(act), narration_text=text)
            
            # ASSET RUNTIME ROUTING: Safely migrate Kokoro's output to the compiler's expected dir
            if os.path.exists(temp_generated_path):
                shutil.move(temp_generated_path, wav_path)
                print(f"    [SUCCESS] Audio tracked moved to target destination: {wav_path}")
            else:
                raise FileNotFoundError(f"Expected generated asset not found at {temp_generated_path}")
            
        print("[SUCCESS] Fresh, clean narration tracks generated and locked.")
    except Exception as audio_err:
        print(f"[CRITICAL FAILURE] Voice synthesis module run failed: {str(audio_err)}")
        sys.exit(1)

    # ==============================================================================
    # PHASE 2: GENERATE THE DYNAMIC VISUAL CHART SEQUENCE
    # ==============================================================================
    print("\n=== GENERATING TELEMETRY VISUAL FRAMES ===")
    try:
        # Load data values dynamically from the manifest contract
        act2 = next(item for item in manifest_data["timeline"] if item["act"] == 2)
        act3 = next(item for item in manifest_data["timeline"] if item["act"] == 3)
        overlay = act3["data_overlays"][0]
        
        # Calculate exactly how long the chart sequence needs to play across both acts
        chart_start_time = act2["start_time"]       # 15.0
        chart_end_time = act3["end_time"]           # 50.0
        total_chart_duration = chart_end_time - chart_start_time # Exactly 35 seconds
        
        # Calculate exactly when the visual spike should occur
        # Trigger time is 38.0. Chart starts at 15.0. 38.0 - 15.0 = 23.0 seconds!
        visual_anomaly_second = overlay["trigger_time"] - chart_start_time
        
        # Construct the DataFrame step matrix dynamically
        total_steps = int(total_chart_duration) # 35 tracking steps
        anomaly_index = int(visual_anomaly_second) # Index 23
        
        # Build clean date ranges spanning the precise duration
        dates = pd.date_range(start="2026-06-01", periods=total_steps, freq='D')
        
        np.random.seed(42)
        base_costs = 150.0 + np.random.normal(0, 4, total_steps)
        
        # Plant the anomaly marker exactly where the manifest dictates
        base_costs[anomaly_index] += 135.0  
        
        telemetry_df = pd.DataFrame({
            'log_timestamp': dates,
            'infrastructure_fee_usd': base_costs
        })
        
        telemetry_df['is_anomaly'] = False
        telemetry_df.loc[anomaly_index, 'is_anomaly'] = True
        
        # Run the visual renderer with 1 second per step to match the timeline layout
        chart_engine = TelemetryChartEngine()
        frames_dir = chart_engine.render_sequenced_frames(telemetry_df, fps=30, secs_per_day=1.0)
        print(f"[SUCCESS] Visual sequence assets locked down inside: {frames_dir}")
        
    except Exception as e:
        print(f"[CRITICAL FAILURE] Visual frame step crashed: {str(e)}")
        sys.exit(1)

    # ==============================================================================
    # PHASE 3: MASTER TIMELINE COMPILER & RENDER
    # ==============================================================================
    print("\n=== STARTING MASTER RENDER TEST ===")
    try:
        compiler = MoviePyTimelineCompiler(episode_num=EPISODE_NUM)
        print("[SUCCESS] Timeline compiler initialized with backend specifications.")
        
        output_filename = os.path.join(base_dir, "output", f"episode_{EPISODE_NUM}_master.mp4")
        compiler.execute_master_render(output_filename=output_filename)
        
        print(f"\n=== SPRINT COMPLETED SUCCESSFULLY ===")
        print(f"Master render compiled to: {output_filename}")
        
    except Exception as e:
        print(f"\n[CRITICAL FAILURE] Render pipeline halted: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()