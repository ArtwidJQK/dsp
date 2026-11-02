import winsound
import time
import serial
import sys

def capture_frames(duration=3.0):
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
                    text = line.decode('utf-8', errors='replace')
                    buf.append(text)
                except Exception:
                    pass
    return "".join(buf)

def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else 'quiet'
    
    if mode == 'quiet':
        print("=== TEST A: QUIET ROOM ===")
        time.sleep(0.5)
        out = capture_frames(3.0)
        print(out)
    elif mode == 'noise':
        print("=== TEST B: RANDOM NOISE ===")
        winsound.PlaySound('random_noise.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        time.sleep(1.0)
        out = capture_frames(3.0)
        winsound.PlaySound(None, 0)
        print(out)
    elif mode == 'sine_5cm':
        print("=== TEST C: 440 HZ SINE AT 5 CM ===")
        winsound.PlaySound('sine_440hz.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        time.sleep(1.0)
        out = capture_frames(3.0)
        winsound.PlaySound(None, 0)
        print(out)
    elif mode == 'sine_10cm':
        print("=== TEST D: 440 HZ SINE AT 10 CM ===")
        winsound.PlaySound('sine_440hz.wav', winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
        time.sleep(1.0)
        out = capture_frames(3.0)
        winsound.PlaySound(None, 0)
        print(out)

if __name__ == '__main__':
    main()
