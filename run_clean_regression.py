import serial
import time
import winsound
import re
import numpy as np
import json
import os

NOTES_TO_TEST = [
    {
        'name': 'A4',
        'target_hz': 440.00,
        'wav': 'real_piano_A4.wav',
    },
    {
        'name': 'C4',
        'target_hz': 261.63,
        'wav': 'real_piano_C4.wav',
    },
    {
        'name': 'E3',
        'target_hz': 164.81,
        'wav': 'real_piano_E3.wav',
    },
    {
        'name': 'C5',
        'target_hz': 523.25,
        'wav': 'real_piano_C5.wav',
    },
    {
        'name': 'E2',
        'target_hz': 82.41,
        'wav': 'phone_piano_E2.wav',
    },
]

def parse_frame_block(block_text):
    data = {
        'frame': None,
        'frequency': 0.0,
        'note': 'N/A',
        'valid': False,
        'confidence': 0.0,
        'estimator': 'UNKNOWN'
    }
    
    m = re.search(r'FRAME #(\d+)', block_text)
    if m:
        data['frame'] = int(m.group(1))
        
    m = re.search(r'State:\s*(\w+)', block_text)
    if m:
        state = m.group(1)
        data['valid'] = (state == 'VALID_PITCH')
        
    m = re.search(r'Final Frequency\s*:\s*([\d\.]+)\s*Hz', block_text)
    if m:
        data['frequency'] = float(m.group(1))
        
    m = re.search(r'Final Note\s*:\s*([^\s\(]+)', block_text)
    if m:
        data['note'] = m.group(1)
        
    m = re.search(r'Confidence\s*:\s*([\d\.]+)\s*%', block_text)
    if m:
        data['confidence'] = float(m.group(1))
        
    m = re.search(r'Estimator Mode\s*:\s*([^\r\n]+)', block_text)
    if m:
        data['estimator'] = m.group(1).strip()
        
    return data

def run_test():
    print("======================================================================")
    print("STARTING CLEAN REAL ACOUSTIC PIANO REGRESSION (20 FRAMES PER NOTE)")
    print("======================================================================")
    
    ser = serial.Serial('COM3', 115200, timeout=0.1)
    ser.reset_input_buffer()
    time.sleep(0.5)
    
    all_results = []
    
    for item in NOTES_TO_TEST:
        note_name = item['name']
        target_hz = item['target_hz']
        wav_file = os.path.abspath(item['wav'])
        
        print(f"\n" + "#"*70)
        print(f"TESTING NOTE: {note_name} (Target: {target_hz:.2f} Hz) | WAV: {item['wav']}")
        print("#"*70)
        
        # Start sound loop
        winsound.PlaySound(wav_file, winsound.SND_ASYNC | winsound.SND_LOOP)
        
        # Step 1: Wait until detector responds
        print(">>> Waiting for detector to respond to note...")
        ser.reset_input_buffer()
        t_wait_start = time.time()
        responded = False
        
        while time.time() - t_wait_start < 5.0:
            line = ser.readline().decode('utf-8', errors='ignore')
            if 'State: VALID_PITCH' in line or 'RMS Energy Norm : 0.' in line:
                m = re.search(r'RMS Energy Norm\s*:\s*([\d\.]+)', line)
                if m and float(m.group(1)) >= 0.025:
                    responded = True
                    break
            time.sleep(0.01)
            
        print(f">>> Detector responded! Collecting 20 consecutive frames...")
        
        # Step 2: Collect 20 consecutive frames
        frames = []
        current_block = []
        last_frame_id = -1
        
        t_collect_start = time.time()
        while len(frames) < 20 and (time.time() - t_collect_start < 12.0):
            line = ser.readline().decode('utf-8', errors='ignore')
            if not line:
                continue
                
            if '[E2-DIAG FRAME #' in line:
                if current_block:
                    block_str = "".join(current_block)
                    fd = parse_frame_block(block_str)
                    if fd['frame'] is not None and fd['frame'] != last_frame_id:
                        frames.append(fd)
                        last_frame_id = fd['frame']
                        print(f"  Frame {fd['frame']:5} | Valid: {str(fd['valid']):5} | Note: {fd['note']:4} | Freq: {fd['frequency']:7.2f} Hz | Conf: {fd['confidence']:4.0f}% | Est: {fd['estimator']}")
                        if len(frames) >= 20:
                            break
                    current_block = []
            current_block.append(line)
            
        # Parse last block if needed
        if len(frames) < 20 and current_block:
            block_str = "".join(current_block)
            fd = parse_frame_block(block_str)
            if fd['frame'] is not None and fd['frame'] != last_frame_id:
                frames.append(fd)
                print(f"  Frame {fd['frame']:5} | Valid: {str(fd['valid']):5} | Note: {fd['note']:4} | Freq: {fd['frequency']:7.2f} Hz | Conf: {fd['confidence']:4.0f}% | Est: {fd['estimator']}")
                
        # Stop sound
        winsound.PlaySound(None, winsound.SND_PURGE)
        time.sleep(1.5) # Silence cooldown
        
        # Calculate statistics
        total_frames = len(frames)
        correct_frames = [f for f in frames if f['note'] == note_name and f['valid']]
        no_signal_frames = [f for f in frames if not f['valid'] or f['note'] == 'N/A' or f['frequency'] == 0.0]
        
        # Octave errors
        base_char = note_name[:-1]
        target_oct = int(note_name[-1])
        octave_errors = []
        for f in frames:
            n = f['note']
            if f['valid'] and n.startswith(base_char) and len(n) == len(note_name) and n != note_name:
                octave_errors.append(f)
                
        correct_rate = (len(correct_frames) / total_frames * 100.0) if total_frames > 0 else 0.0
        no_sig_rate = (len(no_signal_frames) / total_frames * 100.0) if total_frames > 0 else 0.0
        
        valid_freqs = [f['frequency'] for f in correct_frames]
        if valid_freqs:
            mean_f = float(np.mean(valid_freqs))
            median_f = float(np.median(valid_freqs))
            errors = [abs(f - target_hz) for f in valid_freqs]
            mae = float(np.mean(errors))
            max_err = float(np.max(errors))
            std_f = float(np.std(valid_freqs))
        else:
            mean_f = 0.0
            median_f = 0.0
            mae = 0.0
            max_err = 0.0
            std_f = 0.0
            
        summary = {
            'note': note_name,
            'target_hz': target_hz,
            'total_frames': total_frames,
            'correct_frames': len(correct_frames),
            'correct_rate_pct': correct_rate,
            'no_signal_frames': len(no_signal_frames),
            'no_signal_rate_pct': no_sig_rate,
            'octave_errors_count': len(octave_errors),
            'mean_freq': mean_f,
            'median_freq': median_f,
            'mae': mae,
            'max_error': max_err,
            'std_freq': std_f,
            'frames': frames
        }
        all_results.append(summary)
        
        print("\n" + "-"*50)
        print(f"STATISTICS FOR {note_name}:")
        print(f"  Total Frames        : {total_frames}")
        print(f"  Correct-Note Rate   : {correct_rate:.1f}% ({len(correct_frames)}/{total_frames})")
        print(f"  Mean Frequency      : {mean_f:.3f} Hz (Target: {target_hz:.2f} Hz)")
        print(f"  Median Frequency    : {median_f:.3f} Hz")
        print(f"  MAE                 : {mae:.3f} Hz")
        print(f"  Max Absolute Error  : {max_err:.3f} Hz")
        print(f"  Std Deviation       : {std_f:.3f} Hz")
        print(f"  NO_SIGNAL Rate      : {no_sig_rate:.1f}% ({len(no_signal_frames)}/{total_frames})")
        print(f"  Octave Errors Count : {len(octave_errors)}")
        print("-"*50)
        
    ser.close()
    
    with open('clean_regression_results.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2)
    print("\nSaved full clean regression results to clean_regression_results.json\n")

if __name__ == '__main__':
    run_test()
