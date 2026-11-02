import serial
import time
import re
import sys
import numpy as np

def parse_stream(raw_text):
    frames = []
    # Split by frame header
    chunks = re.split(r'>>> \[FRAME #(\d+) \| (\w+)\] <<<', raw_text)
    # chunks[0] is header/garbage, then groups of 3: (num, state, body)
    i = 1
    while i < len(chunks) - 2:
        frame_num = int(chunks[i])
        state = chunks[i+1]
        body = chunks[i+2]
        i += 3
        
        frame_data = {
            'num': frame_num,
            'state': state,
            'raw_body': body.strip()
        }
        
        m = re.search(r'1\. AC RMS\s+:\s+([\d\.]+)\s+counts \(norm:\s+([\d\.]+)\)', body)
        if m:
            frame_data['ac_rms_counts'] = float(m.group(1))
            frame_data['ac_rms_norm'] = float(m.group(2))
            
        m = re.search(r'2\. Maximum FFT Magnitude\s+:\s+([\d\.]+)\s+\(Bin (\d+) = ([\d\.]+) Hz\)', body)
        if m:
            frame_data['max_mag'] = float(m.group(1))
            frame_data['max_bin'] = int(m.group(2))
            frame_data['max_freq'] = float(m.group(3))
            
        m = re.search(r'3\. Candidate Frequency\s+:\s+([\d\.]+) Hz \(Bin (\d+)\)', body)
        if m:
            frame_data['cand_freq'] = float(m.group(1))
            frame_data['cand_bin'] = int(m.group(2))
            
        m = re.search(r'4\. Candidate Magnitude\s+:\s+([\d\.]+)', body)
        if m:
            frame_data['cand_mag'] = float(m.group(1))
            
        m = re.search(r'5\. Local Noise Floor\s+:\s+([\d\.]+)', body)
        if m:
            frame_data['local_floor'] = float(m.group(1))
            
        m = re.search(r'6\. Spectral Prominence/SNR\s+:\s+([\d\.]+)\s+x\s+\(\s*([+-]?[\d\.]+)\s+dB\)', body)
        if m:
            frame_data['prominence'] = float(m.group(1))
            frame_data['prominence_db'] = float(m.group(2))
            
        m = re.search(r'7\. Harmonic Score\s+:\s+([\d\.]+)\s+\(Harmonics verified: (\d+)\)', body)
        if m:
            frame_data['harmonic_score'] = float(m.group(1))
            frame_data['harmonics_found'] = int(m.group(2))
            
        m = re.search(r'9\. Estimated Pitch \(f0 QI\)\s+:\s+([\d\.]+) Hz \(Interpolation p = ([+-]?[\d\.]+)\)', body)
        if m:
            frame_data['f0'] = float(m.group(1))
            frame_data['p'] = float(m.group(2))
        else:
            frame_data['f0'] = None
            frame_data['p'] = None
            
        frames.append(frame_data)
    return frames

def collect_from_serial(duration=4.0):
    port = 'COM3'
    baud = 115200
    with serial.Serial(port, baud, timeout=0.1) as ser:
        ser.reset_input_buffer()
        start = time.time()
        buf = []
        while time.time() - start < duration:
            line = ser.readline()
            if line:
                try:
                    buf.append(line.decode('utf-8', errors='replace'))
                except Exception:
                    pass
    return "".join(buf)

if __name__ == '__main__':
    raw = collect_from_serial(3.0)
    parsed = parse_stream(raw)
    print(f"Collected {len(parsed)} frames.")
    for f in parsed[:3]:
        print(f['num'], f['state'], f.get('cand_mag'), f.get('f0'))
