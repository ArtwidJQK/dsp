import os
import sys
import time
import json
import threading
import urllib.request
import winsound
import numpy as np

TARGET_NOTES = {
    "A4": 440.000,
    "C4": 261.626,
    "E3": 164.814,
}

TEST_FILES = [
    ("A4", "real_piano_A4.wav"),
    ("C4", "real_piano_C4.wav"),
    ("E3", "real_piano_E3.wav"),
]

def play_audio(wav_path, stop_event):
    while not stop_event.is_set():
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)

def test_note(note_name, wav_file, capture_target=15, duration=6.0):
    wav_path = os.path.abspath(wav_file)
    target_hz = TARGET_NOTES[note_name]
    print(f"\n" + "="*70)
    print(f"TESTING REAL ACOUSTIC PIANO NOTE: {note_name} (Target: {target_hz:.3f} Hz)")
    print(f"Audio Source: {wav_file} (Acoustic Piano Recording)")
    print("="*70)
    
    stop_event = threading.Event()
    t_play = threading.Thread(target=play_audio, args=(wav_path, stop_event))
    t_play.daemon = True
    t_play.start()
    
    # Allow acoustic strike to reach INMP441
    time.sleep(0.3)
    
    url = "http://192.168.1.238/api/data"
    t_start = time.time()
    captured_frames = []
    seen_frame_ids = set()
    
    while (time.time() - t_start < duration) and len(captured_frames) < capture_target:
        try:
            req = urllib.request.Request(url)
            with urllib.request.urlopen(req, timeout=0.8) as r:
                data = json.loads(r.read().decode('utf-8'))
                f_id = data.get('frame')
                if f_id not in seen_frame_ids:
                    seen_frame_ids.add(f_id)
                    if data.get('valid') and data.get('frequency', 0.0) > 10.0:
                        captured_frames.append(data)
                        note_det = data.get('note')
                        freq_det = data.get('frequency')
                        cents_det = data.get('cents')
                        est_det = data.get('estimator')
                        conf_det = data.get('confidence')
                        lat_det = data.get('latency_ms')
                        match_str = "[OK]" if note_det == note_name else "[MISMATCH]"
                        print(f"  Frame {f_id:5} | {match_str:10} | Note: {note_det:4} | Freq: {freq_det:7.2f} Hz | Cents: {cents_det:+6.2f} | Est: {est_det:12} | Conf: {conf_det:4.0f}% | Lat: {lat_det:.1f}ms")
        except Exception as e:
            pass
        time.sleep(0.09)
        
    stop_event.set()
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass
        
    time.sleep(0.2)
    
    total = len(captured_frames)
    correct_frames = [f for f in captured_frames if f.get('note') == note_name]
    correct_cnt = len(correct_frames)
    correct_rate = (correct_cnt / total * 100.0) if total > 0 else 0.0
    
    freqs = [f['frequency'] for f in correct_frames]
    cents = [f['cents'] for f in correct_frames]
    
    mean_f = float(np.mean(freqs)) if freqs else 0.0
    std_f = float(np.std(freqs)) if freqs else 0.0
    errors = [abs(f - target_hz) for f in freqs]
    mae = float(np.mean(errors)) if errors else 0.0
    max_err = float(np.max(errors)) if errors else 0.0
    mean_cents = float(np.mean(cents)) if cents else 0.0
    
    est_counts = {}
    for f in captured_frames:
        est = f.get('estimator', 'UNKNOWN')
        est_counts[est] = est_counts.get(est, 0) + 1
        
    all_notes = [f.get('note') for f in captured_frames]
    
    summary = {
        'note': note_name,
        'target_hz': target_hz,
        'total_captured': total,
        'correct_frames': correct_cnt,
        'correct_rate_pct': correct_rate,
        'mean_freq': mean_f,
        'std_freq': std_f,
        'mae': mae,
        'max_error': max_err,
        'mean_cents': mean_cents,
        'estimators': est_counts,
        'all_detected_notes': list(set(all_notes)),
        'frames': captured_frames
    }
    
    print("-" * 70)
    print(f"SUMMARY FOR {note_name}:")
    print(f"  Captured: {total} frames | Correct: {correct_cnt}/{total} ({correct_rate:.1f}%)")
    print(f"  Mean Freq: {mean_f:.3f} Hz (Target: {target_hz:.3f} Hz, Diff: {mean_f - target_hz:+.3f} Hz)")
    print(f"  MAE: {mae:.3f} Hz | Max Error: {max_err:.3f} Hz | Std: {std_f:.3f} Hz | Mean Cents: {mean_cents:+.2f}")
    print(f"  Estimator Breakdown: {est_counts}")
    print("=" * 70)
    return summary

def main():
    print("STARTING REAL ACOUSTIC PIANO VALIDATION TEST (STABLE BASELINE RESTORED)")
    results = []
    for note_name, wav_file in TEST_FILES:
        res = test_note(note_name, wav_file, capture_target=15, duration=6.0)
        if res:
            results.append(res)
        time.sleep(1.0)
        
    with open('verified_stable_baseline_test.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    print("\nSaved full results to verified_stable_baseline_test.json")

if __name__ == '__main__':
    main()
