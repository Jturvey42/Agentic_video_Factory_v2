import pandas as pd
import numpy as np

# All imports cleanly managed at the top of the file scope
from prosody_engine import AudioProsodyEngine
from financial_sentinel import FinancialSentinel
from visual_manifest import VisualManifestGenerator
from layout_engine_v2 import TelemetryLayoutEngineV2
from manifest_compiler import ManifestCompiler

def run_pipeline_test():
    print("=== STEP 1: TESTING AUDIO PROSODY PIPELINE ===")
    audio_engine = AudioProsodyEngine()
    raw_script_line = "We are diving backend-first into the architecture... checking our logs—everything is escalating quickly!"
    clean_text = audio_engine.preprocess_text(raw_script_line)
    print(f"Punctuation Padded Text:\n   '{clean_text}'\n")

    print("=== STEP 2: TESTING PREDICTABLE WEEKLY CYCLES ===")
    
    # 1. Create a 21-day timeline (3 full weeks, starting on a Monday)
    dates = pd.date_range(start="2026-06-01", periods=21, freq='D')
    
    # 2. Build a predictable weekly pattern based on the day of the week (0=Monday, 6=Sunday)
    weekly_cycle = []
    for d in dates:
        day_num = d.dayofweek
        if day_num in [1, 2, 3]:   # Tuesday, Wednesday, Thursday (Peak Usage)
            cycle_modifier = 50.0
        elif day_num in [5, 6]:    # Saturday, Sunday (Low Idle Usage)
            cycle_modifier = -20.0
        else:                      # Monday, Friday (Transition Days)
            cycle_modifier = 0.0
        weekly_cycle.append(cycle_modifier)
        
    # 3. Combine baseline cost ($150) + weekly predictable wave + random daily noise
    np.random.seed(42)
    base_cost = 150.0
    noise = np.random.normal(loc=0, scale=3, size=21)
    total_costs = base_cost + np.array(weekly_cycle) + noise
    
    # 4. Inject a TRUE structural anomaly on Day 18 (Thursday of Week 3)
    total_costs[17] += 120.0  
    
    mock_logs = pd.DataFrame({
        'log_timestamp': dates,
        'infrastructure_fee_usd': total_costs
    })
    
    # 5. Run the sentinel pipeline with a 7-day lookback window
    sentinel = FinancialSentinel(window_size=7, threshold=2.0)
    processed_telemetry = sentinel.process_cost_telemetry(
        raw_log_df=mock_logs, 
        timestamp_col='log_timestamp', 
        cost_col='infrastructure_fee_usd'
    )
    
    # Print out results grouped by week
    columns_to_show = ['log_timestamp', 'infrastructure_fee_usd', 'z_score', 'is_anomaly']
    
    print("--- WEEK 1: BASELINE ESTABLISHMENT ---")
    print(processed_telemetry[columns_to_show].iloc[0:7].to_string(index=False))
    
    print("\n--- WEEK 2: SYSTEM RUNNING WITH CYCLE PATTERN ---")
    print(processed_telemetry[columns_to_show].iloc[7:14].to_string(index=False))
    
    print("\n--- WEEK 3: SYSTEM CONTAINING UNEXPECTED SPIKE ---")
    print(processed_telemetry[columns_to_show].iloc[14:21].to_string(index=False))
    
    print("\n=== STEP 3: TESTING VISUAL MANIFEST GENERATION ===")
    visual_engine = VisualManifestGenerator(fps=30)
    manifest = visual_engine.generate_scene_manifest(processed_telemetry)
    
    normal_day_manifest = manifest[7]   # Week 2 Monday
    anomaly_day_manifest = manifest[17] # Week 3 Thursday (The spike day)
    
    print(f"--- Visual Instructions for Normal Day ({normal_day_manifest['timeline_date']}) ---")
    print(f"  Line Color:      {normal_day_manifest['visual_states']['line_color']}")
    print(f"  Indicator Radius:{normal_day_manifest['visual_states']['chart_indicator_radius']}px")
    print(f"  Text Animation:  {normal_day_manifest['visual_states']['text_animation']}")
    print(f"  Audio Ducking:   {normal_day_manifest['audio_instructions']['ducking_profile']}")
    
    print(f"\n--- Visual Instructions for Anomaly Day ({anomaly_day_manifest['timeline_date']}) ---")
    print(f"  Line Color:      {anomaly_day_manifest['visual_states']['line_color']}")
    print(f"  Indicator Radius:{anomaly_day_manifest['visual_states']['chart_indicator_radius']}px")
    print(f"  Text Animation:  {anomaly_day_manifest['visual_states']['text_animation']}")
    print(f"  Audio Ducking:   {anomaly_day_manifest['audio_instructions']['ducking_profile']}")

    print("\n=== STEP 4: TESTING LAYOUT ENGINE SPEC GENERATION ===")
    layout_engine = TelemetryLayoutEngineV2()
    
    normal_render_spec = layout_engine.generate_frame_render_spec(normal_day_manifest, frame_number=7)
    anomaly_render_spec = layout_engine.generate_frame_render_spec(anomaly_day_manifest, frame_number=17)
    
    print(f"--- Render Spec for Normal Day ({normal_render_spec['typography']['date_label']['text']}) ---")
    print(f"  BG Alert Opacity:  {normal_render_spec['background']['alert_opacity']}")
    print(f"  Chart Node Radius: {normal_render_spec['chart_ui']['target_node']['radius']}px")
    print(f"  Cost Label Pos:    X={normal_render_spec['typography']['cost_readout']['x']}, Y={normal_render_spec['typography']['cost_readout']['y']}")
    print(f"  Audio Command:     {normal_render_spec['audio_mixing']['ducking_profile']}")
    
    print(f"\n--- Render Spec for Anomaly Day ({anomaly_render_spec['typography']['date_label']['text']}) ---")
    print(f"  BG Alert Opacity:  {anomaly_render_spec['background']['alert_opacity']:.4f}")
    print(f"  Chart Node Radius: {anomaly_render_spec['chart_ui']['target_node']['radius']}px")
    print(f"  Cost Label Pos:    X={anomaly_render_spec['typography']['cost_readout']['x']}, Y={anomaly_render_spec['typography']['cost_readout']['y']} (Glitch Shifted)")
    print(f"  Audio Command:     {anomaly_render_spec['audio_mixing']['ducking_profile']}")

    print("\n=== STEP 5: MANIFEST COMPILATION ===")
    # Extract structural anomalies directly from Step 2's data frame safely inside function scope
    detected_anomalies = []
    
    # Grab row index 17 (Day 18) directly from the processed telemetry
    day_18_row = processed_telemetry.iloc[17]
    
    if day_18_row['is_anomaly']:
        detected_anomalies.append({
            "timestamp": 17 * 5.0,  # 5 seconds per sequence index day
            "duration": 4.5,
            "z_score": float(day_18_row['z_score']),
            "amount_spiked": 120.0
        })

    # Pull configuration directly from your verified layout engine specs
    if detected_anomalies:
        layout_spec = {
            "source_file": "financial_sentinel.py",
            "position": [anomaly_render_spec['typography']['cost_readout']['x'], anomaly_render_spec['typography']['cost_readout']['y']],
            "opacity": 1.0,
            "alert_color": "#FF1111",
            "glitch_fx": {
                "coordinate_shake": True,
                "shake_intensity": 12
            },
            "min_opacity": 0.2,
            "max_opacity": float(anomaly_render_spec['background']['alert_opacity'])
        }
    else:
        layout_spec = {
            "source_file": "financial_sentinel.py",
            "position": ["center", "center"],
            "opacity": 0.95,
            "alert_color": "#00FF66",
            "glitch_fx": {"coordinate_shake": False},
            "min_opacity": 0.95,
            "max_opacity": 0.95
        }

    # Compile the layout specs to json
    compiler = ManifestCompiler()
    scene_1 = compiler.compile_scene(
        scene_id=2,
        start=60.0,
        end=90.0,
        bg_source="assets/video/cloud_infrastructure_broll.mp4",
        layout_spec=layout_spec,
        anomalies=detected_anomalies
    )

    manifest_data = {
        "meta": compiler.build_meta(total_duration=120.0),
        "audio_tracks": compiler.build_audio_tracks(
            voiceover_path="output/audio/episode2_voiceover.wav",
            ducking_profile=anomaly_render_spec['audio_mixing']['ducking_profile'] if detected_anomalies else "standard"
        ),
        "timeline": [scene_1]
    }

    saved_path = compiler.export_manifest(manifest_data)
    print(f" SUCCESS: Backend outputs mapped to manifest. Day 18 anomaly tracked.\n File saved to: {saved_path}")

# ==========================================
# EXECUTION ENTRY POINT
# ==========================================
if __name__ == "__main__":
    run_pipeline_test()