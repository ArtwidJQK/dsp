import serial
import time
import subprocess
import sys

def main():
    port = 'COM3'
    print(f"Connecting to {port} to trigger bootloader mode...")
    try:
        s = serial.Serial(port, 115200)
        s.dtr = False
        s.rts = True
        time.sleep(0.2)
        s.dtr = True
        time.sleep(0.1)
        s.rts = False
        time.sleep(0.5)
        s.dtr = False
        s.close()
    except Exception as e:
        print(f"Serial boot trigger note: {e}")
    time.sleep(0.3)

    print("Flashing piano_tuner.bin...")
    bin_path = r"D:\dsp\artwid\piano_tuner\build\piano_tuner.bin"
    python_idf = r"C:\Users\dxem1\.espressif\python_env\idf6.0_py3.14_env\Scripts\python.exe"
    cmd = [
        python_idf, "-m", "esptool",
        "--chip", "esp32s3",
        "-p", port,
        "-b", "460800",
        "--before", "no-reset",
        "--after", "hard-reset",
        "write-flash", "0x10000", bin_path
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("esptool failed!")
        sys.exit(res.returncode)

    print("Hard resetting into application...")
    try:
        s = serial.Serial(port, 115200)
        s.dtr = False
        s.rts = True
        time.sleep(0.1)
        s.rts = False
        time.sleep(0.5)
        s.close()
    except Exception as e:
        print(f"Serial app reset note: {e}")
    print("Done flashing and reset!")

if __name__ == '__main__':
    main()
