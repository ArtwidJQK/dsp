import serial
import time
import sys
import os
import re

def record_piano_note(note_name="E2", port='COM3', baud=115200, max_wait_sec=60, capture_duration=15, out_file='real_piano_log.txt'):
    print(f"\n>>> [RECORDER]: Đang lắng nghe trên {port} cho nốt {note_name}...")
    print(f">>> HÃY ĐÁNH NỐT {note_name} TRÊN ĐÀN PIANO THẬT NGAY BÂY GIỜ VÀ GIỮ PHÍM NGÂN TỰ NHIÊN! <<<")
    print(f">>> (Chương trình tự động bắt đầu thu ngay khi phát hiện lực đánh phím)\n")
    
    collected_lines = []
    triggered = False
    trigger_start_time = 0
    start_wait = time.time()
    
    try:
        with serial.Serial(port, baud, timeout=0.1) as ser:
            ser.reset_input_buffer()
            while True:
                now = time.time()
                if not triggered and (now - start_wait > max_wait_sec):
                    print(f"\n[HẾT THỜI GIAN CHỜ {max_wait_sec}s]: Chưa phát hiện tiếng đàn. Kết thúc.")
                    break
                
                if triggered and (now - trigger_start_time > capture_duration):
                    print(f"\n[HOÀN TẤT THU]: Đã thu xong {capture_duration}s cho nốt {note_name}.")
                    break
                    
                line = ser.readline()
                if not line:
                    continue
                try:
                    text = line.decode('utf-8', errors='replace')
                except Exception:
                    continue
                    
                # Kiểm tra trigger đánh nốt (RMS năng lượng hoặc khung E2-DIAG / VALID_PITCH)
                if not triggered:
                    if "[E2-DIAG FRAME #" in text or "VALID_PITCH" in text:
                        # Kiểm tra xem có năng lượng vượt trội không
                        triggered = True
                        trigger_start_time = time.time()
                        print(f"\n>>> [ĐÃ BẮT ĐƯỢC TÍN HIỆU ĐÀN!] Bắt đầu ghi dữ liệu {capture_duration}s...\n")
                
                if triggered:
                    sys.stdout.write(text)
                    sys.stdout.flush()
                    collected_lines.append(text)
                else:
                    # In 1 dòng tóm tắt chờ
                    if "Listening..." in text:
                        sys.stdout.write(".")
                        sys.stdout.flush()
    except Exception as e:
        print(f"Lỗi Serial: {e}")
        return []
        
    with open(out_file, 'w', encoding='utf-8') as f:
        f.writelines(collected_lines)
    print(f"\nĐã lưu {len(collected_lines)} dòng log thực tế vào {out_file}\n")
    return collected_lines

if __name__ == '__main__':
    note = sys.argv[1] if len(sys.argv) > 1 else "E2"
    out = sys.argv[2] if len(sys.argv) > 2 else f"real_piano_{note}_log.txt"
    dur = float(sys.argv[3]) if len(sys.argv) > 3 else 12.0
    record_piano_note(note_name=note, out_file=out, capture_duration=dur)
