import numpy as np

Fs = 16000
N = 4096
bin_res = Fs / N

def calculate_local_noise_floor(mag, bin_idx):
    neighbors = []
    left_start = max(7, bin_idx - 12)
    left_end = max(7, bin_idx - 3)
    for k in range(left_start, left_end + 1):
        neighbors.append(mag[k])
    right_start = min(len(mag) - 1, bin_idx + 3)
    right_end = min(len(mag) - 1, bin_idx + 12)
    for k in range(right_start, right_end + 1):
        neighbors.append(mag[k])
    if len(neighbors) == 0: return 0.2
    neighbors.sort()
    med = neighbors[len(neighbors)//2]
    return max(0.05, med)

def evaluate_harmonic_hypothesis(mag, hyp_f):
    if hyp_f < 27.5 or hyp_f > 4186.0:
        return 0.0, 0, 0, 0
    hyp_k = hyp_f / bin_res
    h_count = 0
    h_mask = 0
    total_energy = 0.0
    dominant_bin = int(round(hyp_k))
    max_found_mag = 0.0
    
    for m in range(1, 7):
        target_k = int(round(m * hyp_k))
        if target_k >= len(mag) - 2:
            break
        w_start = max(1, target_k - 2)
        w_end = min(len(mag) - 2, target_k + 2)
        
        peak_w = w_start
        max_v = mag[w_start]
        for w in range(w_start + 1, w_end + 1):
            if mag[w] > max_v:
                max_v = mag[w]
                peak_w = w
                
        is_local_peak = (mag[peak_w] >= mag[peak_w - 1] and mag[peak_w] >= mag[peak_w + 1])
        local_floor = calculate_local_noise_floor(mag, peak_w)
        prom = max_v / local_floor
        
        if is_local_peak and prom >= 2.2 and max_v >= 1.0:
            h_count += 1
            h_mask |= (1 << (m - 1))
            total_energy += (1.0 / np.sqrt(m)) * np.log1p(prom) * np.sqrt(max_v)
            if max_v > max_found_mag:
                max_found_mag = max_v
                dominant_bin = peak_w
                
    if h_count == 0:
        return 0.0, 0, 0, dominant_bin
        
    score = total_energy * (1.0 + 0.40 * (h_count - 1))
    
    # Octave-down phantom penalty: if no odd harmonics present (m=1, 3, 5)
    has_odd = (h_mask & 0x15) != 0
    if not has_odd:
        score *= 0.05
    else:
        # If m=1 is missing, check m=2 and m=3
        if (h_mask & 0x01) == 0:
            if (h_mask & 0x02) != 0 and (h_mask & 0x04) != 0:
                score *= 0.85
            else:
                score *= 0.20
                
    # Low frequency penalty (< 110 Hz, k < 28)
    if hyp_k < 28:
        if h_count < 3 or max_found_mag < 14.0:
            score *= 0.10
            
    return score, h_count, h_mask, dominant_bin

def run_pitch_detector(mag):
    # Find candidate peaks
    candidates = []
    for k in range(7, 1072):
        if mag[k] > mag[k-1] and mag[k] > mag[k+1]:
            local_floor = calculate_local_noise_floor(mag, k)
            prom = mag[k] / local_floor
            if mag[k] >= 1.5 and prom >= 2.0:
                candidates.append((k, k * bin_res, mag[k], prom))
                
    if not candidates:
        return None
        
    candidates.sort(key=lambda x: x[2], reverse=True)
    best_cand_peak = candidates[0]
    best_hyp_f = best_cand_peak[1]
    best_hyp_score = -1.0
    best_h_count = 0
    best_h_mask = 0
    best_divisor = 1
    
    # Diagnostic scores for top candidate peak
    diag_f = best_cand_peak[1]
    diag_scores = {}
    for d in [1, 2, 3, 4]:
        hyp_f = diag_f / d
        sc, cnt, mask, dom_bin = evaluate_harmonic_hypothesis(mag, hyp_f)
        diag_scores[d] = (sc, cnt, mask)
        if sc > best_hyp_score:
            best_hyp_score = sc
            best_hyp_f = hyp_f
            best_h_count = cnt
            best_h_mask = mask
            best_divisor = d
            
    for cand in candidates[1:5]:
        for d in [1, 2, 3]:
            hyp_f = cand[1] / d
            sc, cnt, mask, dom_bin = evaluate_harmonic_hypothesis(mag, hyp_f)
            if sc > best_hyp_score:
                best_hyp_score = sc
                best_hyp_f = hyp_f
                best_h_count = cnt
                best_h_mask = mask
                best_divisor = d
                best_cand_peak = cand
                
    # Quadratic Interpolation
    sel_bin = int(round(best_hyp_f / bin_res))
    p = 0.0
    if sel_bin > 0 and sel_bin < len(mag) - 1:
        if mag[sel_bin] >= mag[sel_bin-1] and mag[sel_bin] >= mag[sel_bin+1]:
            alpha = mag[sel_bin-1]
            beta  = mag[sel_bin]
            gamma = mag[sel_bin+1]
            denom = alpha - 2*beta + gamma
            if abs(denom) > 1e-6:
                p = 0.5 * (alpha - gamma) / denom
            raw_f0 = (sel_bin + p) * bin_res
        else:
            cand_bin = best_cand_peak[0]
            alpha = mag[cand_bin-1]
            beta  = mag[cand_bin]
            gamma = mag[cand_bin+1]
            denom = alpha - 2*beta + gamma
            if abs(denom) > 1e-6:
                p = 0.5 * (alpha - gamma) / denom
            raw_f0 = ((cand_bin + p) * bin_res) / best_divisor
            
    h_list = [m for m in range(1, 7) if (best_h_mask & (1 << (m-1)))]
    return {
        'candidate_peak': best_cand_peak[1],
        'cand_mag': best_cand_peak[2],
        'selected_hyp_f': best_hyp_f,
        'divisor': best_divisor,
        'f_score': diag_scores[1][0],
        'f2_score': diag_scores[2][0],
        'f3_score': diag_scores[3][0],
        'final_score': best_hyp_score,
        'h_count': best_h_count,
        'harmonics': h_list,
        'estimated_f0': raw_f0
    }

if __name__ == '__main__':
    test_cases = [
        ('A4 (440.00 Hz)', 440.0, {1: 0.50, 2: 0.15, 3: 0.05}),
        ('C4 (261.63 Hz)', 261.63, {1: 0.15, 2: 0.50, 3: 0.25, 4: 0.12}),
        ('C5 (523.25 Hz)', 523.25, {1: 0.50, 2: 0.20, 3: 0.08}),
    ]

    for name, target_f, weights in test_cases:
        t = np.arange(N) / Fs
        sig = np.zeros_like(t)
        for m, w in weights.items():
            sig += w * np.sin(2 * np.pi * m * target_f * t)
        sig += 0.005 * np.random.randn(len(t))
        window = np.hanning(N)
        mag = np.abs(np.fft.rfft(sig * window))
        
        res = run_pitch_detector(mag)
        print(f"=== {name} ===")
        print(f"Candidate peak     : {res['candidate_peak']:.2f} Hz (Mag: {res['cand_mag']:.2f})")
        print(f"Selected Hypothesis: {res['selected_hyp_f']:.2f} Hz (Divisor: /{res['divisor']})")
        print(f"Hypothesis Scores  : f: {res['f_score']:.1f} | f/2: {res['f2_score']:.1f} | f/3: {res['f3_score']:.1f} | Final: {res['final_score']:.1f}")
        print(f"Harmonics Found    : {res['harmonics']} (Count: {res['h_count']})")
        print(f"Estimated f0 (QI)  : {res['estimated_f0']:.2f} Hz (Expected: {target_f:.2f} Hz)")
        status = 'PASS' if abs(res['estimated_f0'] - target_f) < 2.0 else 'FAIL'
        print(f"Status             : {status}\n")
