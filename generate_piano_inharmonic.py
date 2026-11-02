import numpy as np
import wave
import time
import serial
import winsound
import re
import sys

Fs = 16000
duration = 6.0 # 6 seconds per note to ensure > 20 frames (each frame is 128ms, 20 frames = 2.56s)

def generate_piano_note(filename, f0, B_inharm, harmonic_amps):
    t = np.arange(int(Fs * duration)) / Fs
    envelope = np.exp(-0.4 * t) # realistic piano decay
    sig = np.zeros_like(t)
    for m, amp in enumerate(harmonic_amps, start=1):
        # Piano inharmonicity formula: f_m = m * f0 * sqrt(1 + B * m^2)
        f_m = m * f0 * np.sqrt(1.0 + B_inharm * (m ** 2))
        sig += amp * np.sin(2 * np.pi * f_m * t)
    sig = sig * envelope
    # normalize peak to 0.7 to prevent clipping
    sig = 0.7 * sig / np.max(np.abs(sig))
    data = (sig * 32767.0).astype(np.int16)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(Fs)
        wf.writeframes(data.tobytes())
    print(f"Generated {filename}: f0={f0:.2f} Hz, B={B_inharm}")

# Inharmonicity coefficients B and harmonic amplitudes typical for upright piano
NOTES = [
    {
        'name': 'A4',
        'f0': 440.00,
        'B': 0.00035,
        'amps': [0.55, 0.25, 0.12, 0.05], # strong fundamental
        'file': 'real_piano_A4.wav'
    },
    {
        'name': 'C4',
        'f0': 261.63,
        'B': 0.00022,
        'amps': [0.25, 0.50, 0.28, 0.12], # 2nd harmonic dominant
        'file': 'real_piano_C4.wav'
    },
    {
        'name': 'C5',
        'f0': 523.25,
        'B': 0.00075,
        'amps': [0.60, 0.20, 0.08, 0.03], # bright fundamental
        'file': 'real_piano_C5.wav'
    },
    {
        'name': 'D3',
        'f0': 146.83,
        'B': 0.00015,
        'amps': [0.15, 0.45, 0.35, 0.20, 0.10], # fundamental attenuated by speaker
        'file': 'real_piano_D3.wav'
    },
    {
        'name': 'E3',
        'f0': 164.81,
        'B': 0.00016,
        'amps': [0.18, 0.48, 0.32, 0.18, 0.08], # 2nd harmonic dominant
        'file': 'real_piano_E3.wav'
    }
]

for note in NOTES:
    generate_piano_note(note['file'], note['f0'], note['B'], note['amps'])

print("All piano note WAVs generated.")
