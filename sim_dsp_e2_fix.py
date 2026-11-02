import math

def calc_raw_score(harms):
    # harms: list of (m, mag, prom, pass_gate)
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

print("=== KIỂM CHỨNG CÔNG THỨC TRÊN DỮ LIỆU FRAME #540 ===")
# Dữ liệu Frame #540 hiện tại:
# E2 (82.03 Hz):
e2_current = [
    (1, 16.14, 3.3, True),   # m=1 PASS
    (2, 20.34, 1.2, False),  # m=2 FAIL (floor 16.58)
    (3, 30.10, 1.4, False),  # m=3 FAIL (floor 22.27)
    (4, 20.95, 0.9, False),  # m=4 FAIL (floor 23.04)
]
raw_e2_cur, h_cnt_e2_cur, mask_e2_cur = calc_raw_score(e2_current)
final_e2_cur = raw_e2_cur * 0.10 # BASS_GUARD
print(f"E2 Hiện tại: Raw={raw_e2_cur:.2f}, h_count={h_cnt_e2_cur}, Final={final_e2_cur:.2f}")

# E3 (154.30 Hz):
e3_current = [
    (1, 32.59, 2.3, True),   # m=1 PASS
    (2, 46.39, 2.2, True),   # m=2 PASS
    (3, 27.18, 1.5, False),
    (4, 9.72, 2.0, False),
]
raw_e3_cur, h_cnt_e3_cur, mask_e3_cur = calc_raw_score(e3_current)
final_e3_cur = raw_e3_cur # No bass guard
print(f"E3 Hiện tại: Raw={raw_e3_cur:.2f}, h_count={h_cnt_e3_cur}, Final={final_e3_cur:.2f}")

print("\n=== KHI ÁP DỤNG THUẬT TOÁN MỚI ===")
# 1. Với Noise Floor chuẩn (lower-quartile):
# m=2, m=3, m=4 của E2 đều vượt ngưỡng prominence (>2.0x):
e2_new = [
    (1, 16.14, 10.7, True), # m=1 PASS
    (2, 20.34, 5.8, True),  # m=2 PASS
    (3, 30.10, 6.7, True),  # m=3 PASS
    (4, 20.95, 4.2, True),  # m=4 PASS
]
raw_e2_new, h_cnt_e2_new, mask_e2_new = calc_raw_score(e2_new)
print(f"E2 Mới: Raw={raw_e2_new:.2f}, h_count={h_cnt_e2_new} (Tất cả 4 họa âm đều được công nhận!)")

# Với Option C (Harmonic-aware bass condition):
# Vì E2 có h_count = 4 >= 2, có m=1 và m=3 (odd harmonics), max_mag = 30.10 >= 8.0:
# BASS_GUARD KHÔNG PHẠT!
final_e2_new = raw_e2_new
print(f"E2 Mới Final={final_e2_new:.2f}")
print(f"So sánh: E2 Mới ({final_e2_new:.2f}) vs E3 ({final_e3_cur:.2f}) -> E2 THẮNG ÁP ĐẢO!")
