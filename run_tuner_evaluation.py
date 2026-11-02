import winsound
import time
import serial
import re

PORT = 'COM3'
BAUD = 115200

def test_note(wav_file, label, duration=3.0):
    print(f"\n======================================================================")
    print(f"ĐANG KIỂM THỬ: {label} (Phát: {wav_file})")
    print(f"======================================================================")
    
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
    time.sleep(0.3)
    ser.reset_input_buffer()
    
    # Bắt đầu phát âm thanh
    winsound.PlaySound(wav_file, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)
    start = time.time()
    
    captured_blocks = []
    curr_buf = ""
    
    while time.time() - start < duration:
        line = ser.readline()
        if line:
            text = line.decode('utf-8', errors='replace')
            curr_buf += text
            if "----------------------------------------------------------------------" in curr_buf:
                parts = curr_buf.split("----------------------------------------------------------------------")
                for p in parts[:-1]:
                    if "DSP frame interval" in p and "Candidate Peak" in p:
                        captured_blocks.append(p.strip())
                curr_buf = parts[-1]
                
    winsound.PlaySound(None, 0)
    ser.close()
    time.sleep(0.5)
    
    print(f"Thu thập được {len(captured_blocks)} khung chẩn đoán.")
    # In ra 3-4 khung hợp lệ đại diện
    valid_blocks = [b for b in captured_blocks if "VALID_PITCH" in b]
    if valid_blocks:
        print(f"Khung VALID_PITCH mẫu:")
        for b in valid_blocks[-3:]:
            print("----------------------------------------------------------------------")
            print(b)
    else:
        print("Không có khung VALID_PITCH nào, in các khung cuối:")
        for b in captured_blocks[-2:]:
            print("----------------------------------------------------------------------")
            print(b)
            
    return valid_blocks

if __name__ == '__main__':
    time.sleep(1.0)
    test_note('piano_a4_440hz.wav', 'A4 = 440.00 HZ', 2.8)
    test_note('piano_c4_261hz.wav',  'C4 = 261.63 HZ', 2.8)
    test_note('piano_c5_523hz.wav',  'C5 = 523.25 HZ', 2.8)
