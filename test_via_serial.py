import serial
import time
import winsound
import threading
import os
import re
import json
import numpy as np

PORT = 'COM3'
BAUD = 115200

def parse_diag_frame(block_text):
    f_match = re.search(r'\[(?:E2-DIAG )?FRAME #(\d+)', block_text)
    frame_num = int(f_match.group(1)) if f_match else 0
    
    state_match = re.search(r'State:\s*(\w+)', block_text)
    state = state_match.group(1) if state_match else 'NO_SIGNAL'
    
    rms_match = re.search(r'RMS Energy Norm\s*:\s*([\d\.]+)', block_text)
    rms = float(rms_match.group(1)) if rms_match else 0.0
    
    note_match = re.search(r'Final Note\s*:\s*([A-G]#?\d|N/A)', block_text)
    note = note_match.group(1) if note_match else 'N/A'
    
    freq_match = re.search(r'Final Frequency\s*:\s*([\d\.]+)\s*Hz', block_text)
    freq = float(freq_match.group(1)) if freq_match else 0.0
    
    cents_match = re.search(r'Cents Error\s*:\s*([\+\-]?[\d\.]+)\s*cents', block_text)
    cents = float(cents_match.group(1)) if cents_match else 0.0
    
    est_match = re.search(r'Estimator Mode\s*:\s*(\w+)', block_text)
    est = est_match.group(1) if est_match else 'INVALID'
    
    conf_match = re.search(r'Confidence\s*:\s*([\d\.]+)%', block_text)
    conf = float(conf_match.group(1)) if conf_match else 0.0
    
    # Check simple line format if not diag block: "[FRAME #... | NO_SIGNAL] Listening..."
    if not note_match:
        simple_match = re.search(r'\[FRAME #(\d+) \| (\w+)\]', block_text)
        if simple_match:
            frame_num = int(simple_match.group(1))
            state = simple_match.group(2)
            note = 'N/A'
            freq = 0.0
            est = 'NO_SIGNAL'
            
    return {
        'frame': frame_num,
        'state': state,
        'valid': (state == 'VALID_PITCH'),
        'note': note,
        'frequency': freq,
        'cents': cents,
        'estimator': est,
        'confidence': conf,
        'rms': rms
    }

def play_audio(wav_path, stop_event):
    while not stop_event.is_set():
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)

def test_silence(ser, duration=3.0):
    print("\n" + "="*70)
    print("TESTING SILENCE / AMBIENT NOISE OVER COM3 (HUM & NOISE PROTECTION)")
    print("="*70)
    ser.reset_input_buffer()
    t_start = time.time()
    frames = []
    
    curr_lines = []
    while time.time() - t_start < duration:
        line = ser.readline()
        if not line:
            continue
        try:
            text = line.decode('utf-8', errors='replace')
        except Exception:
            continue
            
        if "=== [E2-DIAG FRAME #" in text or "Listening..." in text:
            if curr_lines:
                parsed = parse_diag_frame("".join(curr_lines))
                if parsed and parsed.get('frame', 0) > 0:
                    frames.append(parsed)
                    v_str = "[VALID!]" if parsed['valid'] else "[CLEAN]"
                    print(f"  Frame {parsed['frame']:5} | {v_str:7} | Note: {parsed['note']:4} | Freq: {parsed['frequency']:6.2f}Hz | State: {parsed['state']} | Est: {parsed['estimator']}")
                curr_lines = []
        curr_lines.append(text)
        
    if curr_lines:
        parsed = parse_diag_frame("".join(curr_lines))
        if parsed and parsed.get('frame', 0) > 0:
            frames.append(parsed)
            
    total = len(frames)
    fps = sum(1 for f in frames if f['valid'])
    fp_rate = (fps / total * 100.0) if total > 0 else 0.0
    print(f"Silence Summary: Total Frames={total}, False Positives={fps}, FP Rate={fp_rate:.1f}%")
    return {'total': total, 'false_positives': fps, 'fp_rate_pct': fp_rate}

def test_note_serial(ser, note_name, wav_file, target_hz, duration=5.5):
    wav_path = os.path.abspath(wav_file)
    print("\n" + "="*70)
    print(f"TESTING NOTE: {note_name} (Target: {target_hz:.3f} Hz) via COM3")
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
    
    ser.reset_input_buffer()
    t_start = time.time()
    frames = []
    curr_lines = []
    
    while time.time() - t_start < duration:
        line = ser.readline()
        if not line:
            continue
        try:
            text = line.decode('utf-8', errors='replace')
        except Exception:
            continue
            
        if "=== [E2-DIAG FRAME #" in text or "Listening..." in text:
            if curr_lines:
                parsed = parse_diag_frame("".join(curr_lines))
                if parsed and parsed.get('frame', 0) > 0:
                    frames.append(parsed)
                    match_str = "[OK]" if parsed['note'] == note_name else ("[NO_SIG]" if not parsed['valid'] else "[MISMATCH]")
                    print(f"  Frame {parsed['frame']:5} | {match_str:10} | Note: {parsed['note']:4} | Freq: {parsed['frequency']:7.2f} Hz | Cents: {parsed['cents']:+6.2f} | Est: {parsed['estimator']:12} | Conf: {parsed['confidence']:4.0f}% | State: {parsed['state']}")
                curr_lines = []
        curr_lines.append(text)
        
    stop_event.set()
    try:
        winsound.PlaySound(None, winsound.SND_PURGE)
    except Exception:
        pass
        
    if curr_lines:
        parsed = parse_diag_frame("".join(curr_lines))
        if parsed and parsed.get('frame', 0) > 0:
            frames.append(parsed)
            
    total = len(frames)
    correct_frames = [f for f in frames if f.get('note') == note_name]
    no_sig_frames = [f for f in frames if not f.get('valid')]
    
    # Octave error detection
    base_char = note_name[:-1]
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
    print(f"Opening {PORT} at {BAUD} baud...")
    with serial.Serial(PORT, BAUD, timeout=0.1) as ser:
        results = {}
        # 1. Silence test
        results['silence'] = test_silence(ser, 3.0)
        
        # 2. Test notes
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
            res = test_note_serial(ser, n, f, hz, duration=5.5)
            if res:
                note_results.append(res)
            time.sleep(0.5)
            
        results['notes'] = note_results
        
        with open('bass_fix_test_results.json', 'w', encoding='utf-8') as out_fp:
            json.dump(results, out_fp, indent=2)
        print("\nSaved all serial results to bass_fix_test_results.json")

if __name__ == '__main__':
    main()
