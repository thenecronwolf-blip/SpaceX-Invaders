"""
generate_audio.py
-----------------
Generates streamer-safe synthwave music and sound effects.
Run once to regenerate assets/music.wav, shoot.wav, explosion.wav
"""

import os
import math
import wave
import struct
import random

SAMPLE_RATE = 44100
ASSETS_DIR = "assets"

os.makedirs(ASSETS_DIR, exist_ok=True)

def write_wav(path, samples):
    with wave.open(path, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(SAMPLE_RATE)
        for s in samples:
            wf.writeframes(
                struct.pack("<h", int(max(-1, min(1, s)) * 32767))
            )

# ---------------- SYNTHWAVE MUSIC ----------------
duration = 30  # seconds
music_samples = []

for i in range(SAMPLE_RATE * duration):
    t = i / SAMPLE_RATE
    bass = math.sin(2 * math.pi * 110 * t) * 0.4
    pad = math.sin(2 * math.pi * 220 * t) * 0.2
    wobble = math.sin(2 * math.pi * (110 + 20 * math.sin(t)) * t) * 0.2
    music_samples.append(bass + pad + wobble)

write_wav(f"{ASSETS_DIR}/music.wav", music_samples)

# ---------------- LASER SFX ----------------
laser_samples = []
for i in range(int(SAMPLE_RATE * 0.15)):
    t = i / SAMPLE_RATE
    s = math.sin(2 * math.pi * 880 * t) * (1 - t * 6)
    laser_samples.append(s)

write_wav(f"{ASSETS_DIR}/shoot.wav", laser_samples)

# ---------------- EXPLOSION SFX ----------------
explosion_samples = []
for i in range(int(SAMPLE_RATE * 0.5)):
    t = i / SAMPLE_RATE
    noise = random.uniform(-1, 1)
    explosion_samples.append(noise * (1 - t * 2))

write_wav(f"{ASSETS_DIR}/explosion.wav", explosion_samples)

print("Audio assets generated successfully.")
