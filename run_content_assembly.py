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
from src.goal_tracker_ui import generate_polished_hud

def main():
    # --------------------------------------------------------------------------
    # CONFIGURATION CONTROL PANEL
    # --------------------------------------------------------------------------
    # TARGETING EPISODE 3 (Global Supply Shock Engine)
    EPISODE_NUM = 3 
    
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

    # Load the manifest data layout explicitly
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest_data = json.load(f)

    # ==============================================================================
    # PHASE 1: AUTOMATED NARRATION BUILDER & GOAL TRACKER HUD ENGINE
    # ==============================================================================
    print("\n=== GENERATING SANITIZED NARRATION AUDIO & MILESTONE HUD FRAMES ===")
    try:
        from tools import generate_scene_audio  
        
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
        
        milestones = manifest_data.get("milestones", [])
        scenes = manifest_data.get("scenes", [])
        
        # Loop through Episode 3's Scenes array 
        for scene in scenes:
            scene_id = scene["scene_id"]
            title = scene["title"]
            text = scene["audio_script"]
            active_milestone_id = scene["visual_layers"]["hud_highlight"]
            
            print(f"\n[➔] Processing Scene {scene_id}: {title}")
            
            # --- PART A: AUDIO GENERATION ---
            wav_name = f"ep3_{scene_id}_narration.wav"
            wav_path = os.path.join(narration_output_dir, wav_name)
            
            numeric_id = int(''.join(filter(str.isdigit, scene_id)))
            temp_generated_path = generate_scene_audio(act_id=numeric_id, narration_text=text)
            
            if os.path.exists(temp_generated_path):
                shutil.move(temp_generated_path, wav_path)
                print(f"    [SUCCESS] Audio tracked moved to: {wav_path}")
            else:
                raise FileNotFoundError(f"Expected generated asset not found at {temp_generated_path}")
            
            # --- PART B: DYNAMIC TEMP MANIFEST GENERATION ---
            print(f"    [HUD] Mutating state structure for focus target: {active_milestone_id}")
            mutated_milestones = []
            
            for ms in milestones:
                ms_copy = ms.copy()
                
                # Critical Alignment: Map "text" to "name" for goal_tracker_ui compatibility
                if "text" in ms_copy and "name" not in ms_copy:
                    ms_copy["name"] = ms_copy["text"]
                
                # Evaluate process state flow mechanics
                if ms_copy["id"] == active_milestone_id:
                    ms_copy["status"] = "active"
                elif int(ms_copy["id"][1:]) < int(active_milestone_id[1:]):
                    ms_copy["status"] = "completed"
                else:
                    ms_copy["status"] = "pending"
                mutated_milestones.append(ms_copy)
            
            # Construct a layout schema structure matching goal_tracker_ui expectations
            temp_manifest_data = {
                "metadata": {"title": manifest_data.get("title", "ECONOMIC ENGINE")},
                "milestones": mutated_milestones
            }
            
            # Write out the temporary file on disk
            temp_manifest_path = os.path.join(base_dir, "data", f"temp_manifest_{scene_id}.json")
            with open(temp_manifest_path, 'w', encoding='utf-8') as temp_f:
                json.dump(temp_manifest_data, temp_f, indent=2)
            
            # --- PART C: EXECUTE THE HUD IMAGE DRAW ---
            output_hud_path = os.path.join(base_dir, "data", f"milestone_hud_{scene_id}.png")
            
            # Pass the manifest path string and output location directly
            generate_polished_hud(temp_manifest_path, output_hud_path)
            
            # Clean up the temporary structural file to keep the folder clean
            try:
                os.remove(temp_manifest_path)
            except OSError:
                pass
                
        print("\n[SUCCESS] Fresh narration tracks and dynamic HUD layouts locked down.")
    except Exception as err:
        print(f"[CRITICAL FAILURE] Asset pipeline assembly failed: {str(err)}")
        sys.exit(1)

    # ==============================================================================
    # PHASE 2: GENERATE THE DYNAMIC VISUAL CHART SEQUENCE
    # ==============================================================================
    print("\n=== GENERATING ECONOMICS TELEMETRY VISUAL FRAMES ===")
    try:
        from src.chart_overlay_engine import TelemetryChartEngine
        
        # 1. Initialize the engine to write directly to our Episode 3 directory
        chart_dir = os.path.join(base_dir, "data", "charts_ep3")
        chart_engine = TelemetryChartEngine(output_dir=chart_dir)
        
        # 2. Recreate the chronological step matrix to match our 33.43-second timeline duration
        total_steps = 35 
        anomaly_index = 15  # Day 15 is where the chokepoint closes and rates spike
        
        dates = pd.date_range(start="2026-06-01", periods=total_steps, freq='D')
        np.random.seed(42)
        base_rates = 1800.0 + np.random.normal(0, 15, total_steps)
        
        # Apply the compounding freight rate curve post-shock
        for t in range(total_steps):
            if t >= anomaly_index:
                time_elapsed = t - anomaly_index
                base_rates[t] += 350 * (time_elapsed ** 1.3)
        
        telemetry_df = pd.DataFrame({
            'log_timestamp': dates,
            'infrastructure_fee_usd': base_rates
        })
        telemetry_df['is_anomaly'] = False
        telemetry_df.loc[anomaly_index, 'is_anomaly'] = True
        
        # 3. Render out the frame array sequence
        chart_engine.render_sequenced_frames(telemetry_df, fps=30, secs_per_day=1.0)
        print(f"[SUCCESS] Visual sequence assets locked down inside: {chart_dir}")
        
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