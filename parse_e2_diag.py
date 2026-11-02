import sys
import re

def parse_diag_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
        
    frames = re.split(r"={10,}\s*\[E2-DIAG FRAME #(\d+)\]\s*={10,}", content)
    if len(frames) <= 1:
        print("Không tìm thấy block E2-DIAG nào trong file.")
        return
        
    print(f"Tổng số frame E2-DIAG tìm thấy: {len(frames)//2}")
    
    for i in range(1, len(frames), 2):
        frame_num = frames[i]
        block = frames[i+1]
        
        # Lấy thông tin cơ bản
        rms_m = re.search(r"RMS Energy Norm\s*:\s*([\d\.]+).*State:\s*(\w+)", block)
        state = rms_m.group(2) if rms_m else "UNKNOWN"
        rms = float(rms_m.group(1)) if rms_m else 0.0
        
        final_m = re.search(r"Best Hyp Freq\s*:\s*([\d\.]+)\s*Hz.*Estimator Mode\s*:\s*(\w+).*Raw f0\s*:\s*([\d\.]+)\s*Hz.*Final Note\s*:\s*(\S+)\s*\(MIDI\s*(\d+).*Cents Error\s*:\s*([\+\-\d\.]+)", block, re.DOTALL)
        
        final_note = final_m.group(4) if final_m else "N/A"
        raw_f0 = float(final_m.group(3)) if final_m else 0.0
        cents = float(final_m.group(6)) if final_m else 0.0
        
        # Chỉ in các frame có liên quan hoặc tóm tắt
        print(f"\n--- FRAME #{frame_num} | State: {state} | Final Note: {final_note} ({raw_f0:.2f} Hz, {cents:+.1f}c) ---")
        
        # In so sánh E2 vs E3
        cmp_m = re.search(r"--- \[E2 \(82.4 Hz\) vs E3 \(164.8 Hz\) COMPARISON\] ---(.*?)(?:D\. Final Decision|$)", block, re.DOTALL)
        if cmp_m:
            cmp_text = cmp_m.group(1).strip()
            print(cmp_text)

if __name__ == '__main__':
    fname = sys.argv[1] if len(sys.argv) > 1 else "real_piano_E2_log.txt"
    parse_diag_file(fname)
