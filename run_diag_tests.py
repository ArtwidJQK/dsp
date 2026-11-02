import winsound
import time
import serial
import re
import numpy as np

def generate_wavs():
    import wave
    fs = 16000
    t = np.linspace(0, 30, fs * 30, endpoint=False)
    
    # 5cm sine wave (matches ~8.9 - 14 mag)
    s_5cm = (0.50 * np.sin(2 * np.pi * 440.0 * t) * 32767).astype(np.int16)
    with wave.open('sine_440hz_5cm.wav', 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(fs)
        f.writeframes(s_5cm.tobytes())
        
    # 10cm sine wave (matches ~4.6 - 6.0 mag)
    s_10cm = (0.25 * np.sin(2 * np.pi * 440.0 * t) * 32767).astype(np.int16)
    with wave.open('sine_440hz_10cm.wav', 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(fs)
        f.writeframes(s_10cm.tobytes())
        
    # 20cm sine wave (matches ~4.8 - 5.1 mag)
    s_20cm = (0.20 * np.sin(2 * np.pi * 440.0 * t) * 32767).astype(np.int16)
    with wave.open('sine_440hz_20cm.wav', 'wb') as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(fs)
        f.writeframes(s_20cm.tobytes())

def capture_serial(duration=4.0):
    port = 'COM3'
    baud = 115200
    lines = []
    with serial.Serial(port, baud, timeout=0.1) as ser:
        ser.reset_input_buffer()
        start = time.time()
        while time.time() - start < duration:
            line = ser.readline()
            if line:
                try:
                    lines.append(line.decode('utf-8', errors='replace'))
                except Exception:
                    pass
    return "".join(lines)

def parse_frames(raw_text):
    frames = []
    chunks = re.split(r'>>> \[FRAME #(\d+) \| (\w+)\] <<<', raw_text)
    i = 1
    while i < len(chunks) - 2:
        frame_num = int(chunks[i])
        state = chunks[i+1]
        body = chunks[i+2]
        i += 3
        
        f = {'num': frame_num, 'state': state, 'raw': body.strip()}
        
        m = re.search(r'1\. AC RMS Normalized\s+:\s+([\d\.]+)', body)
        if m: f['ac_rms_norm'] = float(m.group(1))
        
        m = re.search(r'2\. AC Peak Normalized\s+:\s+([\d\.]+)', body)
        if m: f['ac_peak_norm'] = float(m.group(1))
        
        m = re.search(r'3\. FFT Mag at Bin 113\s+:\s+([\d\.]+)', body)
        if m: f['mag_113'] = float(m.group(1))
        
        m = re.search(r'4\. Local Noise Floor \(113\)\s+:\s+([\d\.]+)', body)
        if m: f['floor_113'] = float(m.group(1))
        
        m = re.search(r'5\. SNR dB at Bin 113\s+:\s+([+-]?[\d\.]+)\s+dB', body)
        if m: f['snr_db'] = float(m.group(1))
        
        m = re.search(r'6\. I2S Slot Status\s+:\s+Left:\s+(\d+)/(\d+)\s+\(([\d\.]+)%\)\s+\|\s+Right:\s+(\d+)/(\d+)\s+\(([\d\.]+)%\)', body)
        if m:
            f['left_nz'] = int(m.group(1))
            f['left_pct'] = float(m.group(3))
            f['right_nz'] = int(m.group(4))
            f['right_pct'] = float(m.group(6))
            
        m = re.search(r'7\. Maximum FFT Magnitude\s+:\s+([\d\.]+)\s+\(Bin (\d+)', body)
        if m:
            f['max_mag'] = float(m.group(1))
            f['max_bin'] = int(m.group(2))
            
        m = re.search(r'9\. QI Estimated f0\s+:\s+([\d\.]+)\s+Hz\s+\(p = ([+-]?[\d\.]+)\)', body)
        if m:
            f['f0'] = float(m.group(1))
            f['p'] = float(m.group(2))
            
        if 'ac_rms_norm' in f and 'mag_113' in f:
            frames.append(f)
    return frames

def print_stats(name, frames):
    print(f"\n=======================================================")
    print(f"BÁO CÁO THỐNG KÊ: {name}")
    print(f"Tổng số frame phân tích: {len(frames)}")
    print(f"=======================================================")
    
    rms = [f['ac_rms_norm'] for f in frames]
    peak = [f['ac_peak_norm'] for f in frames]
    mag = [f['mag_113'] for f in frames]
    floor = [f['floor_113'] for f in frames]
    snr = [f['snr_db'] for f in frames]
    l_pct = [f['left_pct'] for f in frames]
    r_pct = [f['right_pct'] for f in frames]
    
    print(f"{'Thông số':<26} | {'Mean':>10} | {'Min':>10} | {'Max':>10}")
    print(f"{'-'*26}-+-{'-'*10}-+-{'-'*10}-+-{'-'*10}")
    print(f"{'AC RMS Normalized':<26} | {np.mean(rms):>10.6f} | {np.min(rms):>10.6f} | {np.max(rms):>10.6f}")
    print(f"{'AC Peak Normalized':<26} | {np.mean(peak):>10.6f} | {np.min(peak):>10.6f} | {np.max(peak):>10.6f}")
    print(f"{'FFT Mag at Bin 113':<26} | {np.mean(mag):>10.2f} | {np.min(mag):>10.2f} | {np.max(mag):>10.2f}")
    print(f"{'Local Noise Floor (113)':<26} | {np.mean(floor):>10.2f} | {np.min(floor):>10.2f} | {np.max(floor):>10.2f}")
    print(f"{'SNR dB at Bin 113':<26} | {np.mean(snr):>9.2f} dB | {np.min(snr):>9.2f} dB | {np.max(snr):>9.2f} dB")
    print(f"{'Left Slot Active %':<26} | {np.mean(l_pct):>9.1f} % | {np.min(l_pct):>9.1f} % | {np.max(l_pct):>9.1f} %")
    print(f"{'Right Slot Active %':<26} | {np.mean(r_pct):>9.1f} % | {np.min(r_pct):>9.1f} % | {np.max(r_pct):>9.1f} %")
    print()
    
    print("--- 10 Frame liên tiếp chi tiết ---")
    for f in frames[:10]:
        print(f"[# {f['num']}] RMS_norm={f['ac_rms_norm']:.6f} | Peak_norm={f['ac_peak_norm']:.6f} | "
              f"Mag113={f['mag_113']:5.2f} | Floor={f['floor_113']:4.2f} | SNR={f['snr_db']:+6.2f}dB | "
              f"Slot L={f['left_pct']:.1f}% R={f['right_pct']:.1f}%")

def run_case_a():
    print("\n>>> BẮT ĐẦU TEST A: PHÒNG YÊN TĨNH (KHÔNG CÓ 440 HZ) <<<")
    time.sleep(1.0)
    raw = capture_serial(4.5)
    frames = parse_frames(raw)
    print_stats("TEST A: PHÒNG YÊN TĨNH (QUIET ROOM)", frames)
    return frames

def run_case_b():
    print("\n>>> BẮT ĐẦU TEST B: LOA PHÁT SINE 440 HZ Ở 5 CM <<<")
    winsound.PlaySound('sine_440hz_5cm.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    time.sleep(1.5)
    raw = capture_serial(4.5)
    winsound.PlaySound(None, 0)
    frames = parse_frames(raw)
    print_stats("TEST B: SINE 440 HZ Ở 5 CM", frames)
    return frames

def run_case_c():
    print("\n>>> BẮT ĐẦU TEST C: LOA PHÁT SINE 440 HZ Ở 10 CM <<<")
    winsound.PlaySound('sine_440hz_10cm.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    time.sleep(1.5)
    raw = capture_serial(4.5)
    winsound.PlaySound(None, 0)
    frames = parse_frames(raw)
    print_stats("TEST C: SINE 440 HZ Ở 10 CM", frames)
    return frames

def run_case_d():
    print("\n>>> BẮT ĐẦU TEST D: LOA PHÁT SINE 440 HZ Ở 20 CM <<<")
    winsound.PlaySound('sine_440hz_20cm.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    time.sleep(1.5)
    raw = capture_serial(4.5)
    winsound.PlaySound(None, 0)
    frames = parse_frames(raw)
    print_stats("TEST D: SINE 440 HZ Ở 20 CM", frames)
    return frames

if __name__ == '__main__':
    generate_wavs()
    print("Generated test audio files.")
    fa = run_case_a()
    time.sleep(1.0)
    fb = run_case_b()
    time.sleep(1.0)
    fc = run_case_c()
    time.sleep(1.0)
    fd = run_case_d()

