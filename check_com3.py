import serial

try:
    s = serial.Serial('COM3', 115200, timeout=0.5)
    s.close()
    print("COM3 is AVAILABLE!")
except Exception as e:
    print(f"COM3 access error: {e}")
