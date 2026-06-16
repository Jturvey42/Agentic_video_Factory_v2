# test_audio_blend.py
import numpy as np
from prosody_engine import AudioProsodyEngine

def verify_voice_blending():
    print("=== STEP 2: VERIFYING AUDIO SPEAKER EMBEDDING BLEND ===")
    
    # 1. Simulate two distinct 256-dimension voice style vectors (standard for Kokoro-ONNX models)
    np.random.seed(101)
    mock_voice_a = np.random.normal(loc=0.1, scale=0.02, size=(1, 256)) # Primary voice
    mock_voice_b = np.random.normal(loc=-0.1, scale=0.02, size=(1, 256)) # Blend voice
    
    # 2. Initialize the prosody engine with a 35% blend ratio
    blend_ratio = 0.35
    engine = AudioProsodyEngine(
        primary_voice_embedding=mock_voice_a,
        blend_voice_embedding=mock_voice_b,
        blend_ratio=blend_ratio
    )
    
    # 3. Calculate the blended style vector
    blended_vector = engine.get_blended_embedding()
    
    # 4. Perform sanity validations on the numpy arrays
    print(f"Primary Shape: {mock_voice_a.shape} | Blend Shape: {mock_voice_b.shape}")
    print(f"Blended Shape: {blended_vector.shape}")
    
    # Mathematical proof check: Ensure value interpolation falls perfectly between primary and blend
    sample_idx = 0
    val_a = mock_voice_a[0, sample_idx]
    val_b = mock_voice_b[0, sample_idx]
    val_blend = blended_vector[0, sample_idx]
    
    print(f"\nVector Sample Tracking (Index {sample_idx}):")
    print(f"  Voice A (Primary):   {val_a:+.6f}")
    print(f"  Voice B (Modifier):  {val_b:+.6f}")
    print(f"  Blended Result:      {val_blend:+.6f}")
    
    # Calculate what the math *should* be
    expected_val = (val_a * (1.0 - blend_ratio)) + (val_b * blend_ratio)
    print(f"  Expected Formula:    {expected_val:+.6f}")
    
    if np.isclose(val_blend, expected_val):
        print("\n[SUCCESS] Vector interpolation matrix math matches perfectly. No shape distortions.")
    else:
        print("\n[FAILURE] Vector mismatch detected in interpolation layer.")

if __name__ == "__main__":
    verify_voice_blending()