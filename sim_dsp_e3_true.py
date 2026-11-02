import math

def calc_raw_score(harms):
    total_energy = 0.0
    h_count = 0
    h_mask = 0
    for m, mag, prom, pass_gate in harms:
        if pass_gate:
            h_count += 1
            h_mask |= (1 << (m - 1))
            total_energy += (1.0 / math.sqrt(m)) * math.log1p(prom) * math.sqrt(mag)
    if h_count == 0:
        return 0.0, 0, 0
    raw_score = total_energy * (1.0 + 0.40 * (h_count - 1))
    return raw_score, h_count, h_mask

print("=== KIỂM CHỨNG KHI ĐÁNH NỐT E3 THẬT (164.8 Hz) ===")
# Khi đánh E3 thật:
# E3 candidate (164.8 Hz):
e3_when_e3_played = [
    (1, 40.0, 10.0, True),  # 164.8 Hz
    (2, 30.0, 8.0, True),   # 329.6 Hz
    (3, 20.0, 6.0, True),   # 494.4 Hz
    (4, 10.0, 4.0, True),   # 659.2 Hz
]
raw_e3, h_cnt_e3, mask_e3 = calc_raw_score(e3_when_e3_played)
print(f"E3 Candidate: Raw={raw_e3:.2f}, h_count={h_cnt_e3}, Mask=0x{mask_e3:02X}")

# E2 candidate (82.4 Hz) khi E3 được đánh:
# m=1 (82.4 Hz) KHÔNG CÓ (chỉ là nhiễu)
# m=2 (164.8 Hz) CÓ (chính là nốt E3)
# m=3 (247.2 Hz) KHÔNG CÓ
# m=4 (329.6 Hz) CÓ (chính là họa âm 2 của E3)
e2_when_e3_played = [
    (1, 0.8, 1.0, False),  # 82.4 Hz (vắng mặt)
    (2, 40.0, 10.0, True), # 164.8 Hz
    (3, 0.6, 1.0, False),  # 247.2 Hz (vắng mặt)
    (4, 30.0, 8.0, True),  # 329.6 Hz
]
raw_e2, h_cnt_e2, mask_e2 = calc_raw_score(e2_when_e3_played)
has_odd_e2 = (mask_e2 & 0x15) != 0
final_e2 = raw_e2 * (1.0 if has_odd_e2 else 0.05) # Phạt nặng nếu hoàn toàn vắng bóng họa âm lẻ
print(f"E2 Candidate: Raw={raw_e2:.2f}, h_count={h_cnt_e2}, Mask=0x{mask_e2:02X}, HasOdd={has_odd_e2}, Final={final_e2:.2f}")

print(f"\nKết quả khi đánh E3: E3 ({raw_e3:.2f}) vs E2 ({final_e2:.2f}) -> E3 THẮNG TUYỆT ĐỐI GẤP {raw_e3/final_e2:.1f} LẦN!")
