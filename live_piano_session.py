import serial
import time
import sys
import os
import re

def capture_session(port='COM3', baud=115200, duration=15, out_filename='real_piano_capture.txt'):
    print(f"\n========================================================")
    print(f"BẮT ĐẦU THU SERIAL TRÊN {port} ({duration} GIÂY)...")
    print(f"HÃY ĐÁNH NỐT TRÊN PIANO THẬT NGAY BÂY GIỜ VÀ GIỮ PHÍM!")
    print(f"========================================================\n")
    
    lines = []
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            ser.reset_input_buffer()
            start_time = time.time()
            while time.time() - start_time < duration:
                raw_line = ser.readline()
                if raw_line:
                    try:
                        text = raw_line.decode('utf-8', errors='replace')
                        sys.stdout.write(text)
                        sys.stdout.flush()
                        lines.append(text)
                    except Exception:
                        pass
    except Exception as e:
        print(f"Lỗi cổng serial {port}: {e}")
        return []

    with open(out_filename, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print(f"\nĐã lưu {len(lines)} dòng vào file: {out_filename}")
    return lines

if __name__ == '__main__':
    dur = 15
    out = 'real_piano_capture.txt'
    if len(sys.argv) > 1:
        dur = float(sys.argv[1])
    if len(sys.argv) > 2:
        out = sys.argv[2]
    capture_session(duration=dur, out_filename=out)
