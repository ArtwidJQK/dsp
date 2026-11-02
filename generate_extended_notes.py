import numpy as np
import wave
import os

Fs = 16000
duration = 6.0 # 6 seconds per note

def generate_piano_note(filename, f0, B_inharm, harmonic_amps):
    t = np.arange(int(Fs * duration)) / Fs
    # Higher notes decay faster, lower notes sustain longer
    decay_rate = 0.25 if f0 < 200 else (0.5 if f0 < 1000 else 1.2)
    envelope = np.exp(-decay_rate * t)
    sig = np.zeros_like(t)
    for m, amp in enumerate(harmonic_amps, start=1):
        f_m = m * f0 * np.sqrt(1.0 + B_inharm * (m ** 2))
        if f_m >= Fs / 2.0: break # Nyquist guard
        sig += amp * np.sin(2 * np.pi * f_m * t)
    sig = sig * envelope
    max_val = np.max(np.abs(sig))
    if max_val > 1e-6:
        sig = 0.75 * sig / max_val
    data = (sig * 32767.0).astype(np.int16)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(Fs)
        wf.writeframes(data.tobytes())
    print(f"Generated {filename}: f0={f0:.2f} Hz, B={B_inharm}")

# 9 benchmark notes covering the full 88-key piano compass
NOTES_EXTENDED = [
    {
        'name': 'A0',
        'f0': 27.500,
        'B': 0.00008,
        'amps': [0.15, 0.40, 0.35, 0.25, 0.18, 0.12],
        'file': 'real_piano_A0.wav'
    },
    {
        'name': 'C2',
        'f0': 65.406,
        'B': 0.00010,
        'amps': [0.20, 0.45, 0.32, 0.22, 0.15, 0.10],
        'file': 'real_piano_C2.wav'
    },
    {
        'name': 'D3',
        'f0': 146.832,
        'B': 0.00015,
        'amps': [0.22, 0.48, 0.30, 0.18, 0.08],
        'file': 'real_piano_D3.wav'
    },
    {
        'name': 'E3',
        'f0': 164.814,
        'B': 0.00016,
        'amps': [0.25, 0.50, 0.28, 0.15, 0.06],
        'file': 'real_piano_E3.wav'
    },
    {
        'name': 'C4',
        'f0': 261.626,
        'B': 0.00022,
        'amps': [0.45, 0.35, 0.18, 0.08],
        'file': 'real_piano_C4.wav'
    },
    {
        'name': 'A4',
        'f0': 440.000,
        'B': 0.00035,
        'amps': [0.65, 0.22, 0.10, 0.04],
        'file': 'real_piano_A4.wav'
    },
    {
        'name': 'C5',
        'f0': 523.251,
        'B': 0.00075,
        'amps': [0.70, 0.18, 0.06, 0.02],
        'file': 'real_piano_C5.wav'
    },
    {
        'name': 'C6',
        'f0': 1046.502,
        'B': 0.00150,
        'amps': [0.85, 0.12, 0.03],
        'file': 'real_piano_C6.wav'
    },
    {
        'name': 'C8',
        'f0': 4186.009,
        'B': 0.00800,
        'amps': [0.95, 0.05],
        'file': 'real_piano_C8.wav'
    }
]

if __name__ == '__main__':
    for n in NOTES_EXTENDED:
        generate_piano_note(n['file'], n['f0'], n['B'], n['amps'])
    print("Extended piano note benchmark set created successfully.")
