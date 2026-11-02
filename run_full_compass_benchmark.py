import os
import sys
import time
import json
import numpy as np
import urllib.request
import winsound

ESP32_URL = "http://192.168.1.238/api/data"

def wait_for_quiet(timeout_sec=4.0):
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        try:
            with urllib.request.urlopen(ESP32_URL, timeout=0.8) as r:
                d = json.loads(r.read().decode('utf-8'))
                if not d.get('valid'):
                    return True
        except Exception:
            pass
        time.sleep(0.12)
    return False

def test_single_note(note_name, ref_freq, wav_path, play_duration=5.0):
    print(f"\n================================================================================")
    print(f">> BENCHMARKING: {note_name:4} | REF: {ref_freq:8.3f} Hz | FILE: {os.path.basename(wav_path)}")
    print(f"================================================================================")
    wait_for_quiet(3.0)
    
    t0 = time.time()
    winsound.PlaySound(wav_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
    
    samples = []
    while time.time() - t0 < play_duration:
        try:
            with urllib.request.urlopen(ESP32_URL, timeout=0.8) as r:
                d = json.loads(r.read().decode('utf-8'))
                if d.get('valid') and d.get('frequency', 0.0) > 10.0:
                    samples.append(d)
        except Exception:
            pass
        time.sleep(0.08)
        
    winsound.PlaySound(None, winsound.SND_PURGE)
    time.sleep(1.2) # Echo settling time
    
    freqs = [s['frequency'] for s in samples]
    latencies = [s.get('latency_ms', 0.0) for s in samples]
    confidences = [s.get('confidence', 0.0) for s in samples]
    estimators = [s.get('estimator', 'N/A') for s in samples]
    detected_notes = [s.get('note', 'N/A') for s in samples]
    
    if len(freqs) == 0:
        print(f"  [RESULT] No valid frames captured (Energy or harmonic gate rejected)")
        return {
            "note": note_name,
            "ref_freq": ref_freq,
            "count": 0,
            "mean_freq": 0.0,
            "std_freq": 0.0,
            "mean_abs_err": 0.0,
            "max_abs_err": 0.0,
            "every_frame_pass_rate": 0.0,
            "dominant_note": "NONE",
            "estimator": "NONE",
            "mean_latency": 0.0
        }
        
    freq_arr = np.array(freqs)
    abs_errors = np.abs(freq_arr - ref_freq)
    pass_under_05 = np.sum(abs_errors < 0.50) / len(abs_errors) * 100.0
    
    res = {
        "note": note_name,
        "ref_freq": ref_freq,
        "count": len(freqs),
        "mean_freq": float(np.mean(freq_arr)),
        "std_freq": float(np.std(freq_arr)),
        "mean_abs_err": float(np.mean(abs_errors)),
        "max_abs_err": float(np.max(abs_errors)),
        "every_frame_pass_rate": float(pass_under_05),
        "dominant_note": max(set(detected_notes), key=detected_notes.count),
        "estimator": max(set(estimators), key=estimators.count),
        "mean_latency": float(np.mean(latencies))
    }
    
    print(f"  Captured frames        : {res['count']}")
    print(f"  Detected Note Name     : {res['dominant_note']}")
    print(f"  Mean Measured Frequency: {res['mean_freq']:8.3f} Hz (Ref: {ref_freq:8.3f} Hz)")
    print(f"  Frequency Std Dev      : {res['std_freq']:8.3f} Hz")
    print(f"  Mean Absolute Error    : {res['mean_abs_err']:8.3f} Hz")
    print(f"  Max Absolute Error     : {res['max_abs_err']:8.3f} Hz")
    print(f"  Every-Frame < 0.5Hz %  : {res['every_frame_pass_rate']:6.1f} %")
    print(f"  Dominant Estimator Mode: {res['estimator']}")
    print(f"  Mean DSP Processing Lat: {res['mean_latency']:6.2f} ms")
    return res

def run_full_compass_suite():
    compass_tests = [
        ("A0",   27.500, "real_piano_A0.wav"),
        ("C2",   65.406, "real_piano_C2.wav"),
        ("D3",  146.832, "real_piano_D3.wav"),
        ("E3",  164.814, "real_piano_E3.wav"),
        ("C4",  261.626, "real_piano_C4.wav"),
        ("A4",  440.000, "real_piano_A4.wav"),
        ("C5",  523.251, "real_piano_C5.wav"),
        ("C6", 1046.502, "real_piano_C6.wav"),
        ("C8", 4186.009, "real_piano_C8.wav")
    ]
    
    results = []
    for name, ref, fname in compass_tests:
        p = os.path.abspath(fname)
        if os.path.exists(p):
            r = test_single_note(name, ref, p)
            results.append(r)
            time.sleep(1.0)
        else:
            print(f"ERROR: File not found: {fname}")
            
    print("\n" + "="*112)
    print("FINAL 88-KEY COMPASS PIANO ACCURACY & PERFORMANCE MATRIX (ESP32-S3 + INMP441 REAL DATA)")
    print("="*112)
    print(f"{'NOTE':5} | {'REF (Hz)':8} | {'MEASURED':9} | {'STD (Hz)':8} | {'MAE (Hz)':8} | {'MAX (Hz)':8} | {'PASS <0.5':9} | {'NOTE DET':8} | {'ESTIMATOR':12} | {'STATUS'}")
    print("-" * 112)
    for r in results:
        if r['count'] == 0:
            status = "NO_SIGNAL"
        elif r['mean_abs_err'] < 0.50:
            status = "PASS (MAE)"
        else:
            status = "OUT_OF_SPEC"
            
        print(f"{r['note']:5} | {r['ref_freq']:8.3f} | {r['mean_freq']:9.3f} | {r['std_freq']:8.3f} | {r['mean_abs_err']:8.3f} | {r['max_abs_err']:8.3f} | {r['every_frame_pass_rate']:8.1f}% | {r['dominant_note']:8} | {r['estimator']:12} | {status}")
    print("="*112)

if __name__ == '__main__':
    run_full_compass_suite()
