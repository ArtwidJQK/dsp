import os
import sys
import time
import json
import threading
import urllib.request
import winsound
import numpy as np

def play_audio_file(wav_path):
    try:
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)
    except Exception as e:
        print(f"Audio playback error for {wav_path}: {e}")

TARGET_NOTES = {
    "D3": 146.832,
    "E3": 164.814,
    "C4": 261.626,
    "A4": 440.000,
    "C5": 523.251
}

TEST_FILES = [
    ("D3", "real_piano_D3.wav"),
    ("E3", "real_piano_E3.wav"),
    ("C4", "real_piano_C4.wav"),
    ("A4", "real_piano_A4.wav"),
    ("C5", "real_piano_C5.wav"),
]

def test_note(note_name, wav_file, duration=5.0):
    wav_path = os.path.abspath(wav_file)
    target_hz = TARGET_NOTES[note_name]
    print(f"\n=======================================================")
    print(f"REGRESSION TEST NOTE: {note_name} (Target: {target_hz:.3f} Hz)")
    print(f"Audio File: {wav_file} (Duration: {duration}s)")
    print(f"=======================================================")
    
    if not os.path.exists(wav_path):
        print(f"ERROR: Audio file {wav_path} not found!")
        return None
        
    t_play = threading.Thread(target=play_audio_file, args=(wav_path,))
    t_play.daemon = True
    t_play.start()
    
    url = "http://192.168.1.238/api/data"
    t_start = time.time()
    frames = []
    
    while time.time() - t_start < duration:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=0.8) as r:
                data = json.loads(r.read().decode('utf-8'))
                if data.get('valid') and data.get('frequency', 0.0) > 10.0:
                    frames.append(data)
                    print(f"  Frame {data.get('frame'):5} | Note: {data.get('note'):4} | Freq: {data.get('frequency', 0.0):7.2f} Hz | Cents: {data.get('cents', 0.0):+6.2f} | Est: {data.get('estimator')} | Conf: {data.get('confidence', 0.0):4.0f}% | Lat: {data.get('latency_ms', 0.0):.1f}ms")
        except Exception:
            pass
        time.sleep(0.08)
        
    print(f"Captured {len(frames)} frames for {note_name}.")
    
    # Analyze results
    freqs = [f['frequency'] for f in frames if f.get('note') == note_name]
    all_notes = [f.get('note') for f in frames]
    octave_errors = 0
    # Check for octave confusion (e.g. note name with different octave number)
    base_char = note_name[:-1]
    expected_octave = int(note_name[-1])
    for n in all_notes:
        if n and n.startswith(base_char) and len(n) == len(note_name):
            try:
                oct = int(n[-1])
                if oct != expected_octave:
                    octave_errors += 1
            except ValueError:
                pass
                
    correct_count = sum(1 for n in all_notes if n == note_name)
    total_valid = len(frames)
    correct_rate = (correct_count / total_valid * 100.0) if total_valid > 0 else 0.0
    
    if freqs:
        mean_freq = float(np.mean(freqs))
        std_freq = float(np.std(freqs, ddof=1)) if len(freqs) > 1 else 0.0
        abs_errs = [abs(f - target_hz) for f in freqs]
        mae = float(np.mean(abs_errs))
        max_err = float(np.max(abs_errs))
        cents_vals = [f['cents'] for f in frames if f.get('note') == note_name]
        mean_cents = float(np.mean(cents_vals))
    else:
        mean_freq = 0.0
        std_freq = 0.0
        mae = 999.0
        max_err = 999.0
        mean_cents = 0.0
        
    summary = {
        "note": note_name,
        "target_hz": target_hz,
        "total_frames": total_valid,
        "correct_frames": correct_count,
        "correct_rate_pct": correct_rate,
        "octave_errors": octave_errors,
        "mean_freq": mean_freq,
        "std_freq": std_freq,
        "mae": mae,
        "max_err": max_err,
        "mean_cents": mean_cents,
        "all_notes_detected": list(set(all_notes))
    }
    print(f"Summary for {note_name}: Mean = {mean_freq:.3f} Hz | MAE = {mae:.3f} Hz | MaxErr = {max_err:.3f} Hz | Correct = {correct_count}/{total_valid} ({correct_rate:.1f}%) | OctaveErr = {octave_errors}")
    return summary

if __name__ == "__main__":
    all_summaries = []
    for note, fname in TEST_FILES:
        res = test_note(note, fname, duration=5.0)
        if res:
            all_summaries.append(res)
        time.sleep(1.2)
        
    with open("regression_results.json", "w", encoding="utf-8") as f:
        json.dump(all_summaries, f, indent=2)
    print("\n\nAll regression tests completed and saved to regression_results.json!")
