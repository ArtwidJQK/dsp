import winsound
import time
import serial
import re
import numpy as np
import sys

NOTES = [
    {'name': 'A4', 'f0': 440.00, 'file': 'real_piano_A4.wav'},
    {'name': 'C4', 'f0': 261.63, 'file': 'real_piano_C4.wav'},
    {'name': 'C5', 'f0': 523.25, 'file': 'real_piano_C5.wav'},
    {'name': 'D3', 'f0': 146.83, 'file': 'real_piano_D3.wav'},
    {'name': 'E3', 'f0': 164.81, 'file': 'real_piano_E3.wav'}
]

def parse_frame_block(block):
    frame_match = re.search(r"FRAME #(\d+)", block)
    note_match = re.search(r"Note:\s*([A-G]#?\d+)", block)
    midi_match = re.search(r"MIDI\s*(\d+)", block)
    target_match = re.search(r"Target\s*([\d\.]+)\s*Hz", block)
    streak_match = re.search(r"Streak:\s*(\d+)/20", block)
    
    est_mode_match = re.search(r"Estimator Mode\s*:\s*(\w+)", block)
    final_f0_match = re.search(r"Final f0\s*:\s*([\d\.]+)\s*Hz", block)
    f1_q_match = re.search(r"F1 Quality\s*:\s*(.+)", block)
    f2_q_match = re.search(r"F2 Quality\s*:\s*(.+)", block)
    f3_q_match = re.search(r"F3 Quality\s*:\s*(.+)", block)
    
    hyp_match = re.search(r"Selected Hypothesis\s*:\s*([\d\.]+)\s*Hz\s*\(Divisor:\s*/(\d+)\)", block)
    
    m1_match = re.search(r"m=1\s*:\s*Bin\s*(\d+)\s*\|\s*Interp f1\s*=\s*([\d\.]+)\s*Hz\s*\|\s*f0/1\s*=\s*([\d\.]+)\s*Hz\s*\|\s*Mag:\s*([\d\.]+)\s*\|\s*p:\s*([\+\-\d\.]+)", block)
    m2_match = re.search(r"m=2\s*:\s*Bin\s*(\d+)\s*\|\s*Interp f2\s*=\s*([\d\.]+)\s*Hz\s*\|\s*f0/2\s*=\s*([\d\.]+)\s*Hz\s*\|\s*Mag:\s*([\d\.]+)\s*\|\s*p:\s*([\+\-\d\.]+)(?:\s*\|\s*Dev vs m=1:\s*([\+\-\d\.]+)\s*Hz)?", block)
    m3_match = re.search(r"m=3\s*:\s*Bin\s*(\d+)\s*\|\s*Interp f3\s*=\s*([\d\.]+)\s*Hz\s*\|\s*f0/3\s*=\s*([\d\.]+)\s*Hz\s*\|\s*Mag:\s*([\d\.]+)\s*\|\s*p:\s*([\+\-\d\.]+)(?:\s*\|\s*Dev vs m=1:\s*([\+\-\d\.]+)\s*Hz)?", block)
    
    mhqi_match = re.search(r"Current MHQI Weighted f0\s*:\s*([\d\.]+)\s*Hz", block)
    cents_match = re.search(r"Cents\s*:\s*([\+\-\d\.]+)\s*cents", block)
    conf_match = re.search(r"Confidence\s*:\s*([\d\.]+)%", block)
    lat_match = re.search(r"DSP Latency\s*:\s*([\d\.]+)\s*ms", block)
    
    if not (frame_match and est_mode_match and final_f0_match):
        return None
        
    res = {
        'frame': int(frame_match.group(1)),
        'note': note_match.group(1) if note_match else 'N/A',
        'midi': int(midi_match.group(1)) if midi_match else 0,
        'target_freq': float(target_match.group(1)) if target_match else 0.0,
        'streak': int(streak_match.group(1)) if streak_match else 0,
        'est_mode': est_mode_match.group(1),
        'final_f0': float(final_f0_match.group(1)),
        'f1_quality': f1_q_match.group(1).strip() if f1_q_match else 'N/A',
        'f2_quality': f2_q_match.group(1).strip() if f2_q_match else 'N/A',
        'f3_quality': f3_q_match.group(1).strip() if f3_q_match else 'N/A',
        'hyp_f0': float(hyp_match.group(1)) if hyp_match else 0.0,
        'divisor': int(hyp_match.group(2)) if hyp_match else 1,
        'cents': float(cents_match.group(1)) if cents_match else 0.0,
        'confidence': float(conf_match.group(1)) if conf_match else 0.0,
        'latency_ms': float(lat_match.group(1)) if lat_match else 0.0,
        'mhqi': float(mhqi_match.group(1)) if mhqi_match else None,
        'm1': None,
        'm2': None,
        'm3': None
    }
    
    if m1_match:
        res['m1'] = {
            'bin': int(m1_match.group(1)),
            'interp_f': float(m1_match.group(2)),
            'f0_div': float(m1_match.group(3)),
            'mag': float(m1_match.group(4)),
            'p': float(m1_match.group(5))
        }
    if m2_match:
        res['m2'] = {
            'bin': int(m2_match.group(1)),
            'interp_f': float(m2_match.group(2)),
            'f0_div': float(m2_match.group(3)),
            'mag': float(m2_match.group(4)),
            'p': float(m2_match.group(5)),
            'dev': float(m2_match.group(6)) if m2_match.group(6) else (float(m2_match.group(3)) - res['m1']['f0_div'] if res['m1'] else 0.0)
        }
    if m3_match:
        res['m3'] = {
            'bin': int(m3_match.group(1)),
            'interp_f': float(m3_match.group(2)),
            'f0_div': float(m3_match.group(3)),
            'mag': float(m3_match.group(4)),
            'p': float(m3_match.group(5)),
            'dev': float(m3_match.group(6)) if m3_match.group(6) else (float(m3_match.group(3)) - res['m1']['f0_div'] if res['m1'] else 0.0)
        }
    return res

def test_note(ser, note_info):
    name = note_info['name']
    target_f0 = note_info['f0']
    wav_file = note_info['file']
    print(f"\n================================================================================")
    print(f"HARDWARE TEST: NOTE {name} (Target: {target_f0:.2f} Hz)")
    print(f"Playing acoustic piano signal {wav_file} to INMP441 microphone...")
    print(f"================================================================================")
    
    winsound.PlaySound(wav_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    time.sleep(0.4)
    
    ser.reset_input_buffer()
    captured_frames = []
    start_time = time.time()
    
    current_block = []
    while len(captured_frames) < 20 and (time.time() - start_time) < 10.0:
        line = ser.readline()
        if line:
            text = line.decode('utf-8', errors='replace')
            sys.stdout.write(text)
            sys.stdout.flush()
            if ">>> [FRAME #" in text:
                if current_block:
                    parsed = parse_frame_block("".join(current_block))
                    if parsed and parsed.get('streak', 0) > 0:
                        captured_frames.append(parsed)
                current_block = [text]
            else:
                current_block.append(text)
                
    if current_block:
        parsed = parse_frame_block("".join(current_block))
        if parsed and parsed.get('streak', 0) > 0 and len(captured_frames) < 20:
            captured_frames.append(parsed)
            
    # Also wait a little bit to capture the hardware summary block if printed
    summary_wait_start = time.time()
    while (time.time() - summary_wait_start) < 1.0:
        line = ser.readline()
        if line:
            text = line.decode('utf-8', errors='replace')
            sys.stdout.write(text)
            sys.stdout.flush()
            
    winsound.PlaySound(None, 0)
    time.sleep(0.5)
    return captured_frames[:20]

def main():
    port = 'COM3'
    baud = 115200
    all_results = {}
    
    with serial.Serial(port, baud, timeout=0.05) as ser:
        for note in NOTES:
            frames = test_note(ser, note)
            all_results[note['name']] = frames
            print(f"\n[INFO] Note {note['name']}: {len(frames)} VALID_PITCH frames successfully captured from hardware.\n")
            time.sleep(1.0)
            
    print("\n\n" + "="*80)
    print("ALL 5 NOTES MEASURED ON HARDWARE. GENERATING AUDIT TABLES...")
    print("="*80)
    
    for note in NOTES:
        name = note['name']
        target = note['f0']
        frames = all_results.get(name, [])
        print(f"\n################################################################################")
        print(f"AUDIT TABLE: NOTE {name} | Target: {target:.2f} Hz | Captured Frames: {len(frames)}/20")
        print(f"################################################################################")
        
        if not frames:
            print("TEST NOT EXECUTED: No valid frames captured.")
            continue
            
        print(f"{'#':<3} | {'Mode':<11} | {'Final f0':<9} | {'Cents':<7} | {'Conf':<6} | {'Lat(ms)':<7} | {'m=1(f1)':<9} | {'m=2(f2/2)':<9} | {'F1 Quality':<30}")
        print("-" * 105)
        
        final_f0_vals = []
        cents_vals = []
        conf_vals = []
        lat_vals = []
        modes = {}
        
        for i, fr in enumerate(frames, start=1):
            m1_s = f"{fr['m1']['f0_div']:.3f}" if fr['m1'] else "N/A"
            m2_s = f"{fr['m2']['f0_div']:.3f}" if fr['m2'] else "N/A"
            print(f"{i:<3} | {fr['est_mode']:<11} | {fr['final_f0']:<9.3f} | {fr['cents']:<+7.2f} | {fr['confidence']:<5.1f}% | {fr['latency_ms']:<7.2f} | {m1_s:<9} | {m2_s:<9} | {fr['f1_quality'][:30]:<30}")
            
            final_f0_vals.append(fr['final_f0'])
            cents_vals.append(fr['cents'])
            conf_vals.append(fr['confidence'])
            lat_vals.append(fr['latency_ms'])
            modes[fr['est_mode']] = modes.get(fr['est_mode'], 0) + 1
            
        print("-" * 105)
        
        mean_f0 = np.mean(final_f0_vals)
        std_f0 = np.std(final_f0_vals, ddof=1) if len(final_f0_vals) > 1 else 0.0
        abs_errors = [abs(f - target) for f in final_f0_vals]
        mean_abs_err = np.mean(abs_errors)
        max_abs_err = np.max(abs_errors)
        mean_cents = np.mean(cents_vals)
        mean_conf = np.mean(conf_vals)
        mean_lat = np.mean(lat_vals)
        
        mode_str = ", ".join([f"{k}: {v}/{len(frames)}" for k, v in modes.items()])
        
        print("HARDWARE STATISTICAL ANALYSIS:")
        print(f"  Target Frequency       : {target:.2f} Hz")
        print(f"  Mean Final f0          : {mean_f0:7.3f} Hz")
        print(f"  StdDev                 : {std_f0:6.3f} Hz")
        print(f"  Mean Absolute Error    : {mean_abs_err:6.3f} Hz")
        print(f"  Maximum Absolute Error : {max_abs_err:6.3f} Hz")
        print(f"  Mean Cents             : {mean_cents:+6.2f} cents")
        print(f"  Estimator Mode         : {mode_str}")
        print(f"  Mean Confidence        : {mean_conf:5.1f}%")
        print(f"  Mean DSP Latency       : {mean_lat:5.2f} ms")
        print(f"  Actual Note Identified : {frames[-1]['note']}")

if __name__ == '__main__':
    main()
