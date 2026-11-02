import urllib.request
import json
import time
import winsound
import threading
import os
import numpy as np

URL = "http://192.168.1.238/api/data"

def test_silence(duration=3.0):
    print("\n" + "="*70)
    print("TESTING SILENCE / NO-NOTE CONDITION (HUM & AMBIENT PROTECTION)")
    print("="*70)
    t_start = time.time()
    frames = []
    seen = set()
    while time.time() - t_start < duration:
        try:
            req = urllib.request.Request(URL)
            with urllib.request.urlopen(req, timeout=0.5) as r:
                d = json.loads(r.read().decode('utf-8'))
                fid = d.get('frame')
                if fid not in seen:
                    seen.add(fid)
                    frames.append(d)
                    print(f"  Frame {fid:5} | Valid: {str(d.get('valid')):5} | Note: {d.get('note'):4} | Freq: {d.get('frequency', 0.0):7.2f} Hz | Est: {d.get('estimator')}")
        except Exception:
            pass
        time.sleep(0.1)
    
    total = len(frames)
    valid_cnt = sum(1 for f in frames if f.get('valid'))
    fp_rate = (valid_cnt / total * 100.0) if total > 0 else 0.0
    print(f"Silence Test Summary: Total={total}, Valid/False-Positives={valid_cnt}, FP Rate={fp_rate:.1f}%")
    return {'total': total, 'false_positives': valid_cnt, 'fp_rate_pct': fp_rate}

def play_audio(wav_path, stop_event):
    while not stop_event.is_set():
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)

def test_single_note(note_name, wav_file, target_hz, duration=5.5):
    wav_path = os.path.abspath(wav_file)
    print("\n" + "="*70)
    print(f"TESTING NOTE: {note_name} (Target: {target_hz:.3f} Hz)")
    print(f"Audio File: {wav_file}")
    print("="*70)
    
    if not os.path.exists(wav_path):
        print(f"File {wav_path} does not exist!")
        return None
        
    stop_event = threading.Event()
    t_play = threading.Thread(target=play_audio, args=(wav_path, stop_event))
    t_play.daemon = True
    t_play.start()
    time.sleep(0.3)
    
    t_start = time.time()
    frames = []
    seen = set()
    
    while time.time() - t_start < duration:
        try:
            req = urllib.request.Request(URL)
            with urllib.request.urlopen(req, timeout=0.5) as r:
                d = json.loads(r.read().decode('utf-8'))
                fid = d.get('frame')
                if fid not in seen:
                    seen.add(fid)
                    frames.append(d)
                    status = "[OK]" if d.get('note') == note_name else ("[NO_SIG]" if not d.get('valid') else "[MISMATCH]")
                    print(f"  Frame {fid:5} | {status:10} | Note: {d.get('note'):4} | Freq: {d.get('frequency', 0.0):7.2f} Hz | Cents: {d.get('cents', 0.0):+6.2f} | Est: {d.get('estimator')} | Conf: {d.get('confidence', 0.0):4.0f}% | Lat: {d.get('latency_ms', 0.0):.1f}ms")
        except Exception:
            pass
        time.sleep(0.09)
        
    stop_event.set()
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass
    time.sleep(0.3)
    
    total = len(frames)
    correct_frames = [f for f in frames if f.get('note') == note_name]
    no_sig_frames = [f for f in frames if not f.get('valid')]
    
    # Octave error detection
    base_char = note_name[:-1]
    expected_oct = int(note_name[-1])
    octave_errors = 0
    for f in frames:
        n = f.get('note', '')
        if f.get('valid') and n.startswith(base_char) and len(n) == len(note_name) and n != note_name:
            octave_errors += 1
            
    freqs = [f['frequency'] for f in correct_frames]
    mae = float(np.mean([abs(f - target_hz) for f in freqs])) if freqs else 0.0
    max_err = float(np.max([abs(f - target_hz) for f in freqs])) if freqs else 0.0
    mean_f = float(np.mean(freqs)) if freqs else 0.0
    
    correct_rate = (len(correct_frames) / total * 100.0) if total > 0 else 0.0
    no_sig_rate = (len(no_sig_frames) / total * 100.0) if total > 0 else 0.0
    
    summary = {
        'note': note_name,
        'target_hz': target_hz,
        'total_frames': total,
        'correct_frames': len(correct_frames),
        'correct_rate_pct': correct_rate,
        'no_signal_frames': len(no_sig_frames),
        'no_signal_rate_pct': no_sig_rate,
        'octave_errors': octave_errors,
        'mean_freq': mean_f,
        'mae': mae,
        'max_error': max_err,
        'all_detected_notes': list(set(f.get('note') for f in frames))
    }
    
    print("-" * 70)
    print(f"Summary for {note_name}: Correct={len(correct_frames)}/{total} ({correct_rate:.1f}%), Mean={mean_f:.2f}Hz, MAE={mae:.2f}Hz, MaxErr={max_err:.2f}Hz, OctaveErr={octave_errors}, NoSig={no_sig_rate:.1f}%")
    print("=" * 70)
    return summary

def main():
    results = {}
    # 1. Silence test
    results['silence'] = test_silence(3.0)
    
    # 2. Test notes with audio files available
    NOTES_TO_TEST = [
        ("A4", "real_piano_A4.wav", 440.000),
        ("C4", "real_piano_C4.wav", 261.626),
        ("E3", "real_piano_E3.wav", 164.814),
        ("D3", "real_piano_D3.wav", 146.832),
        ("C5", "real_piano_C5.wav", 523.251),
        ("E2", "phone_piano_E2.wav", 82.407),
        ("C2", "real_piano_C2.wav", 65.406),
    ]
    
    note_results = []
    for n, f, hz in NOTES_TO_TEST:
        res = test_single_note(n, f, hz, duration=5.5)
        if res:
            note_results.append(res)
        time.sleep(0.5)
        
    results['notes'] = note_results
    
    with open('bass_fix_test_results.json', 'w', encoding='utf-8') as out_fp:
        json.dump(results, out_fp, indent=2)
    print("\nSaved all results to bass_fix_test_results.json")

if __name__ == '__main__':
    main()
