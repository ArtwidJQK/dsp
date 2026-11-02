import winsound
import time
import serial
import re
import numpy as np

def run_test_1():
    wav_file = 'sine_440hz_10cm.wav'
    print(f"Playing {wav_file} (Continuous 440 Hz tone at ~10cm level)...")
    winsound.PlaySound(wav_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    
    # Wait 1.5s for audio output and acoustic field to stabilize
    time.sleep(1.5)
    
    port = 'COM3'
    baud = 115200
    lines = []
    print("Capturing serial output from COM3...")
    with serial.Serial(port, baud, timeout=0.1) as ser:
        ser.reset_input_buffer()
        start = time.time()
        while time.time() - start < 4.5:
            line = ser.readline()
            if line:
                try:
                    lines.append(line.decode('utf-8', errors='replace'))
                except Exception:
                    pass
                    
    winsound.PlaySound(None, 0)
    raw_output = "".join(lines)
    return raw_output

if __name__ == '__main__':
    raw = run_test_1()
    print("--- RAW OUTPUT RECEIVED ---")
    print(raw)
