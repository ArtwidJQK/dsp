import winsound
import time
import serial
import re

def run_test_2():
    wav_file = 'piano_a4_test.wav'
    print(f"Playing {wav_file} (OnlinePianist Piano A4 at normal volume, 10-20cm)...")
    winsound.PlaySound(wav_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    
    # Wait 1.0s for audio to stabilize
    time.sleep(1.0)
    
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
    raw = run_test_2()
    print("--- RAW OUTPUT RECEIVED TEST 2 ---")
    print(raw)
