import numpy as np
import wave

Fs = 16000
duration = 4.0 # 4 seconds

def write_wav(filename, samples):
    samples = np.clip(samples, -1.0, 1.0)
    data = (samples * 32767.0).astype(np.int16)
    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(Fs)
        wf.writeframes(data.tobytes())
    print(f"Created {filename} (Duration: {duration}s)")

t = np.arange(int(Fs * duration)) / Fs

# 1. A4 = 440 Hz
a4_sig = 0.50 * np.sin(2 * np.pi * 440.0 * t) + 0.15 * np.sin(2 * np.pi * 880.0 * t) + 0.05 * np.sin(2 * np.pi * 1320.0 * t)
write_wav("piano_a4_440hz.wav", a4_sig)

# 2. C4 = 261.63 Hz (Realistic small speaker / piano acoustic: 2nd harmonic 523Hz is 2.5x fundamental!)
c4_sig = (0.20 * np.sin(2 * np.pi * 261.63 * t) + 
          0.55 * np.sin(2 * np.pi * 523.25 * t) + 
          0.28 * np.sin(2 * np.pi * 784.88 * t) + 
          0.12 * np.sin(2 * np.pi * 1046.50 * t))
write_wav("piano_c4_261hz.wav", c4_sig)

# 3. C5 = 523.25 Hz (Pure C5)
c5_sig = (0.50 * np.sin(2 * np.pi * 523.25 * t) + 
          0.20 * np.sin(2 * np.pi * 1046.50 * t) + 
          0.08 * np.sin(2 * np.pi * 1569.75 * t))
write_wav("piano_c5_523hz.wav", c5_sig)
