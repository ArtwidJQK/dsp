import serial
import time
import sys

port = 'COM3'
baud = 115200

duration = 5
if len(sys.argv) > 1:
    duration = float(sys.argv[1])

print(f"Reading from {port} for {duration} seconds...")
try:
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
except Exception as e:
    print(f"Error opening serial port: {e}")
