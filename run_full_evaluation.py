import winsound
import time
import serial
import re

PORT = 'COM3'
BAUD = 115200

def parse_block(block_str):
    res = {}
    m_frame = re.search(r"FRAME #(\d+)", block_str)
    if m_frame:
        res['frame'] = int(m_frame.group(1))
    
    m_state = re.search(r"State\s*:\s*(\w+)", block_str)
    if m_state:
        res['state'] = m_state.group(1)
        
    m_interval = re.search(r"DSP frame interval\s*:\s*([\d\.]+)\s*ms", block_str)
    if m_interval:
        res['interval_ms'] = float(m_interval.group(1))
        
    m_latency = re.search(r"Latency:\s*([\d\.]+)\s*ms", block_str)
    if m_latency:
        res['latency_ms'] = float(m_latency.group(1))
        
    m_cand = re.search(r"Candidate\s*:\s*([\d\.]+)\s*Hz\s*\(Bin\s*(\d+),\s*Mag:\s*([\d\.]+)\)", block_str)
    if m_cand:
        res['cand_hz'] = float(m_cand.group(1))
        res['bin'] = int(m_cand.group(2))
        res['mag'] = float(m_cand.group(3))
        
    m_snr = re.search(r"SNR\s*:\s*([\+\-\d\.]+)\s*dB", block_str)
    if m_snr:
        res['snr_db'] = float(m_snr.group(1))
        
    m_prom = re.search(r"Prominence:\s*([\d\.]+)\s*x", block_str)
    if m_prom:
        res['prominence'] = float(m_prom.group(1))
        
    m_floor = re.search(r"Floor:\s*([\d\.]+)", block_str)
    if m_floor:
        res['floor'] = float(m_floor.group(1))
        
    m_conf = re.search(r"Confidence\s*:\s*(\d+)%", block_str)
    if m_conf:
        res['confidence'] = int(m_conf.group(1))
        
    m_f0 = re.search(r"Estimated f0 \(QI\)\s*:\s*([\d\.]+)\s*Hz\s*\(Smooth Median:\s*([\d\.]+)\s*Hz", block_str)
    if m_f0:
        res['f0_raw'] = float(m_f0.group(1))
        res['f0_smooth'] = float(m_f0.group(2))
        
    m_stable = re.search(r"Stable:\s*(\w+)", block_str)
    if m_stable:
        res['stable'] = m_stable.group(1)
        
    m_max = re.search(r"Global Max Peak\s*:\s*([\d\.]+)\s*Hz\s*\(Bin\s*(\d+),\s*Mag:\s*([\d\.]+)\)", block_str)
    if m_max:
        res['max_hz'] = float(m_max.group(1))
        res['max_bin'] = int(m_max.group(2))
        res['max_mag'] = float(m_max.group(3))
        
    return res

def capture_frames(ser, target_count=10, timeout=4.0):
    frames = []
    curr_buf = ""
    start_t = time.time()
    while len(frames) < target_count and (time.time() - start_t) < timeout:
        line = ser.readline()
        if line:
            text = line.decode('utf-8', errors='replace')
            curr_buf += text
            if "----------------------------------------------------------------------" in curr_buf:
                parts = curr_buf.split("----------------------------------------------------------------------")
                for p in parts[:-1]:
                    data = parse_block(p)
                    if 'frame' in data and 'state' in data:
                        frames.append(data)
                        if len(frames) >= target_count:
                            break
                curr_buf = parts[-1]
    return frames

def run_evaluation():
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(0.5)
    ser.reset_input_buffer()
    
    print("=== ĐO 1: PHÒNG YÊN TĨNH (NO_SIGNAL) ===")
    quiet_frames = capture_frames(ser, 10, timeout=4.0)
    print(f"Thu được {len(quiet_frames)} frames yên tĩnh.")
    for f in quiet_frames[:5]:
        print(f"  Frame #{f.get('frame')}: State={f.get('state')} | Interval={f.get('interval_ms')}ms | Max={f.get('max_hz')}Hz (Mag {f.get('max_mag')}) | SNR={f.get('snr_db')}dB")

    distances = [
        ('5 cm', 'sine_440hz_5cm.wav'),
        ('10 cm', 'sine_440hz_10cm.wav'),
        ('20 cm', 'sine_440hz_20cm.wav')
    ]
    
    results = {}
    for label, wav_file in distances:
        print(f"\n=== ĐO {label.upper()}: PHÁT {wav_file} ===")
        winsound.PlaySound(wav_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        # Giả lập âm thanh xuất hiện ngẫu nhiên không đồng bộ với chu kỳ báo cáo
        time.sleep(0.2)
        ser.reset_input_buffer()
        frames = capture_frames(ser, 10, timeout=3.0)
        winsound.PlaySound(None, 0)
        time.sleep(0.4)
        results[label] = frames
        print(f"Thu được {len(frames)} frames tại {label}:")
        for f in frames:
            f0_str = f"{f.get('f0_raw', 0.0):.2f} Hz" if f.get('state') == 'VALID_PITCH' else 'N/A'
            med_str = f"{f.get('f0_smooth', 0.0):.2f} Hz" if f.get('state') == 'VALID_PITCH' else 'N/A'
            print(f"  Frame #{f.get('frame')}: State={f.get('state')} | Interval={f.get('interval_ms')}ms | Latency={f.get('latency_ms')}ms | f0={f0_str} (Med: {med_str}) | SNR={f.get('snr_db')}dB | Conf={f.get('confidence')}%")

    print("\n=== ĐO 5: NỐT NGẮN PIANO STACCATO (PHÁT CHỈ 400 MS) ===")
    winsound.PlaySound('sine_440hz_10cm.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    ser.reset_input_buffer()
    time.sleep(0.40) # chỉ phát 400 ms
    winsound.PlaySound(None, 0)
    staccato_frames = capture_frames(ser, 6, timeout=2.0)
    print(f"Thu được {len(staccato_frames)} frames khi phát nốt 400 ms:")
    for f in staccato_frames:
        f0_str = f"{f.get('f0_raw', 0.0):.2f} Hz" if f.get('state') == 'VALID_PITCH' else 'N/A'
        print(f"  Frame #{f.get('frame')}: State={f.get('state')} | Interval={f.get('interval_ms')}ms | Latency={f.get('latency_ms')}ms | f0={f0_str} | Conf={f.get('confidence')}%")

    ser.close()

if __name__ == '__main__':
    run_evaluation()
