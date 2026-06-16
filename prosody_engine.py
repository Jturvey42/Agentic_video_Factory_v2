# prosody_engine.py
import re
import numpy as np

class AudioProsodyEngine:
    def __init__(self, primary_voice_embedding: np.ndarray = None, blend_voice_embedding: np.ndarray = None, blend_ratio: float = 0.0):
        """
        Initializes the prosody engine with optional embeddings for voice blending.
        """
        self.primary_voice = primary_voice_embedding
        self.blend_voice = blend_voice_embedding
        self.blend_ratio = blend_ratio

    def preprocess_text(self, text: str) -> str:
        """
        Prepares text strings with targeted punctuation padding. 
        This introduces predictable, natural pauses into the TTS generation.
        """
        if not text:
            return ""

        # Normalize any erratic spacing or line breaks down to single spaces
        processed = " ".join(text.split())

        # Replace dramatic punctuation (em-dashes, ellipses) with isolated commas 
        # to trick the model into a natural conversational pause
        processed = re.sub(r'—', ' , ', processed)
        processed = re.sub(r'\.\.\.', ' , ', processed)

        # Pad standard punctuation to give the speech model breathing room
        processed = re.sub(r',', ', ', processed)
        processed = re.sub(r';', ', ', processed)
        
        # Isolate terminal punctuation to anchor the end of phrases distinctly
        processed = re.sub(r'\.', ' . ', processed)
        processed = re.sub(r'\?', ' ? ', processed)
        processed = re.sub(r'!', ' ! ', processed)

        # Final pass to eliminate any double spaces created by the padding logic
        processed = " ".join(processed.split())

        return processed

    def get_blended_embedding(self) -> np.ndarray:
        """
        Calculates a linear interpolation between two voice vectors.
        Returns the primary voice if no blend voice or ratio is provided.
        """
        if self.blend_voice is None or self.blend_ratio == 0.0:
            return self.primary_voice
        
        # Mathematical blend: (Primary * weight) + (Blend * weight)
        blended_embedding = (self.primary_voice * (1.0 - self.blend_ratio)) + (self.blend_voice * self.blend_ratio)
        return blended_embedding