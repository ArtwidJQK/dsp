import os
import sys
import time
import json
import threading
import urllib.request
import winsound

def play_audio(wav_path):
    try:
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)
    except Exception as e:
        print("Audio play error:", e)

def test_note_playback(wav_path, duration_sec=5.0, label=""):
    print(f"\n==================================================")
    print(f"TESTING NOTE: {label} (File: {os.path.basename(wav_path)})")
    print(f"==================================================")
    
    t = threading.Thread(target=play_audio, args=(wav_path,))
    t.daemon = True
    t.start()
    
    url = "http://192.168.1.238/api/data"
    t_start = time.time()
    valid_frames = []
    
    while time.time() - t_start < duration_sec:
        try:
            with urllib.request.urlopen(url, timeout=0.8) as r:
                data = json.loads(r.read().decode('utf-8'))
                if data.get('valid') and data.get('frequency', 0.0) > 10.0:
                    valid_frames.append(data)
                    print(f"  Frame {data.get('frame'):5} | Note: {data.get('note'):4} | Freq: {data.get('frequency', 0.0):7.2f} Hz | Cents: {data.get('cents', 0.0):+6.2f} | Est: {data.get('estimator')} | Conf: {data.get('confidence', 0.0):4.0f}% | Latency: {data.get('latency_ms', 0.0):.1f}ms")
        except Exception as e:
            pass
        time.sleep(0.08)
        
    print(f"Total valid frames captured: {len(valid_frames)}")
    return valid_frames

if __name__ == "__main__":
    test_files = [
        ("A4", "real_piano_A4.wav"),
        ("C4", "real_piano_C4.wav"),
        ("C5", "real_piano_C5.wav"),
        ("D3", "real_piano_D3.wav"),
        ("E3", "real_piano_E3.wav")
    ]
    for note, fname in test_files:
        p = os.path.abspath(fname)
        if os.path.exists(p):
            test_note_playback(p, 4.0, note)
            time.sleep(1.0)
        else:
            print(f"File not found: {p}")
