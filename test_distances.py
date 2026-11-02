import winsound
import time
import serial
import sys

def test_distance(wav_file, label, duration=3.0):
    print(f"\n=======================================================")
    print(f"BẮT ĐẦU ĐO KIỂM: {label}")
    print(f"Phát file: {wav_file}")
    print(f"=======================================================")
    
    winsound.PlaySound(wav_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    # Wait short 300ms to simulate sound starting at any arbitrary moment
    time.sleep(0.3)
    
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
                    text = line.decode('utf-8', errors='replace')
                    sys.stdout.write(text)
                    sys.stdout.flush()
                except Exception:
                    pass
                    
    winsound.PlaySound(None, 0)
    time.sleep(0.5)

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'all'
    if mode in ('5cm', 'all'):
        test_distance('sine_440hz_5cm.wav', '440 HZ TẠI CỰ LY 5 CM', 2.5)
    if mode in ('10cm', 'all'):
        test_distance('sine_440hz_10cm.wav', '440 HZ TẠI CỰ LY 10 CM', 2.5)
    if mode in ('20cm', 'all'):
        test_distance('sine_440hz_20cm.wav', '440 HZ TẠI CỰ LY 20 CM', 2.5)
