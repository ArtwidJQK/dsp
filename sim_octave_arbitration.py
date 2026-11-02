def arbitrate_octave(f_best, score_best, candidates_diag):
    # candidates_diag: list of dicts with test_f, final_score, h_count, h_mask, harms
    # Check if f_best is an octave harmonic of a lower candidate f_sub ≈ f_best / 2
    f_sub_target = f_best / 2.0
    for cand in candidates_diag:
        f_cand = cand['test_f']
        if abs(f_cand - f_sub_target) / f_sub_target < 0.05: # within 5% of f_best / 2
            # Found candidate f_sub!
            # Check if f_sub has independent odd harmonic support (m=1 or m=3)
            m1_ok = cand['harms'][0]['pass_gate']
            m3_ok = cand['harms'][2]['pass_gate']
            m1_mag = cand['harms'][0]['mag']
            m3_mag = cand['harms'][2]['mag']
            
            print(f"Kiểm tra Octave: f_best={f_best:.1f} Hz vs f_sub={f_cand:.1f} Hz")
            print(f"  f_sub m=1: ok={m1_ok}, mag={m1_mag:.2f}")
            print(f"  f_sub m=3: ok={m3_ok}, mag={m3_mag:.2f}")
            
            if (m1_ok and m1_mag >= 2.0) or (m3_ok and m3_mag >= 2.0):
                print(f"  => PHÁT HIỆN HỌA ÂM LẺ ĐỘC LẬP TẠI f_sub HOẶC 3*f_sub!")
                print(f"  => f_best ({f_best:.1f} Hz) CHỈ LÀ HỌA ÂM BẬC 2 CỦA {f_cand:.1f} Hz!")
                print(f"  => TRỌNG TÀI QUYẾT ĐỊNH: CHỌN f_sub ({f_cand:.1f} Hz) LÀM FUNDAMENTAL!")
                return f_cand, cand['final_score']
            else:
                print(f"  => f_sub không có họa âm lẻ độc lập, f_best là nốt thật.")
                return f_best, score_best
    return f_best, score_best

# Test với Frame #540:
cand_e2 = {
    'test_f': 82.03,
    'final_score': 57.71,
    'h_count': 4,
    'h_mask': 0x0F,
    'harms': [
        {'pass_gate': True, 'mag': 16.14}, # m=1
        {'pass_gate': True, 'mag': 20.34}, # m=2
        {'pass_gate': True, 'mag': 30.10}, # m=3
        {'pass_gate': True, 'mag': 20.95}, # m=4
    ]
}
f_res, sc_res = arbitrate_octave(164.06, 17.45, [cand_e2])
print(f"Kết quả trọng tài: {f_res:.1f} Hz")
