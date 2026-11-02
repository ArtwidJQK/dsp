import os
import sys
import time
import json
import numpy as np
import urllib.request
import winsound

ESP32_URL = "http://192.168.1.238/api/data"

def wait_for_quiet(timeout_sec=5.0):
    t0 = time.time()
    while time.time() - t0 < timeout_sec:
        try:
            with urllib.request.urlopen(ESP32_URL, timeout=1.0) as r:
                d = json.loads(r.read().decode('utf-8'))
                if not d.get('valid'):
                    return True
        except Exception:
            pass
        time.sleep(0.15)
    return False

def test_single_note(note_name, ref_freq, wav_path, play_duration=4.5):
    print(f"\n>>> Benchmarking Note: {note_name} | Reference: {ref_freq:.3f} Hz | File: {os.path.basename(wav_path)}")
    wait_for_quiet(3.0)
    
    # Start audio in background
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
        time.sleep(0.09)
        
    winsound.PlaySound(None, winsound.SND_PURGE) # stop audio
    time.sleep(1.0) # allow echo to subside
    
    # Filter samples for this note
    freqs = [s['frequency'] for s in samples]
    latencies = [s.get('latency_ms', 0.0) for s in samples]
    confidences = [s.get('confidence', 0.0) for s in samples]
    estimators = [s.get('estimator', 'N/A') for s in samples]
    
    if len(freqs) == 0:
        print(f"  NO VALID FRAMES CAPTURED for {note_name}")
        return {
            "note": note_name,
            "ref_freq": ref_freq,
            "count": 0,
            "mean_freq": 0.0,
            "std_freq": 0.0,
            "mean_abs_err": 0.0,
            "max_abs_err": 0.0,
            "estimator": "NONE",
            "mean_latency": 0.0
        }
        
    freq_arr = np.array(freqs)
    abs_errors = np.abs(freq_arr - ref_freq)
    
    res = {
        "note": note_name,
        "ref_freq": ref_freq,
        "count": len(freqs),
        "mean_freq": float(np.mean(freq_arr)),
        "std_freq": float(np.std(freq_arr)),
        "mean_abs_err": float(np.mean(abs_errors)),
        "max_abs_err": float(np.max(abs_errors)),
        "estimator": max(set(estimators), key=estimators.count),
        "mean_latency": float(np.mean(latencies))
    }
    
    print(f"  Captured frames : {res['count']}")
    print(f"  Mean Frequency  : {res['mean_freq']:.3f} Hz")
    print(f"  Std Deviation   : {res['std_freq']:.3f} Hz")
    print(f"  Mean Abs Error  : {res['mean_abs_err']:.3f} Hz")
    print(f"  Max Abs Error   : {res['max_abs_err']:.3f} Hz")
    print(f"  Dominant Estimator: {res['estimator']}")
    print(f"  Mean DSP Latency: {res['mean_latency']:.2f} ms")
    return res

def run_all_benchmarks():
    test_cases = [
        ("A4 (Sine Ref)", 440.000, "sine_440hz_10cm.wav"),
        ("A4 (Piano)", 440.000, "real_piano_A4.wav"),
        ("C4 (Piano)", 261.626, "real_piano_C4.wav"),
        ("C5 (Piano)", 523.251, "real_piano_C5.wav"),
        ("D3 (Piano)", 146.832, "real_piano_D3.wav"),
        ("E3 (Piano)", 164.814, "real_piano_E3.wav")
    ]
    
    results = []
    for note, ref, fname in test_cases:
        p = os.path.abspath(fname)
        if os.path.exists(p):
            r = test_single_note(note, ref, p)
            results.append(r)
            time.sleep(1.5)
        else:
            print(f"File not found: {fname}")
            
    print("\n" + "="*80)
    print("FINAL ACCURACY & LATENCY BENCHMARK REPORT (REAL DATA FROM ESP32-S3)")
    print("="*80)
    print(f"{'NOTE':16} | {'REF (Hz)':8} | {'MEAN (Hz)':9} | {'STD (Hz)':8} | {'MAE (Hz)':8} | {'MAX (Hz)':8} | {'FRAMES':6} | {'ESTIMATOR':12} | {'PASS <0.5Hz'}")
    print("-" * 105)
    for r in results:
        passed = "PASS" if r['count'] > 0 and r['mean_abs_err'] < 0.50 else ("FAIL" if r['count'] > 0 else "NO_DATA")
        print(f"{r['note']:16} | {r['ref_freq']:8.3f} | {r['mean_freq']:9.3f} | {r['std_freq']:8.3f} | {r['mean_abs_err']:8.3f} | {r['max_abs_err']:8.3f} | {r['count']:6} | {r['estimator']:12} | {passed}")
    print("="*80)

if __name__ == "__main__":
    run_all_benchmarks()
