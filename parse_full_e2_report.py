import re

with open('verified_real_piano_E2_final.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

blocks = text.split('==================== [E2-DIAG FRAME #')
print(f'Total frames in verified_real_piano_E2_final.txt: {len(blocks)-1}')

results = []
for b in blocks[1:]:
    f_num = b.split(']')[0]
    rms = re.search(r'RMS Energy Norm\s*:\s*([\d\.]+)', b)
    state = re.search(r'State:\s*(\w+)', b)
    note = re.search(r'Final Note\s*:\s*([A-G]#?\d|N/A)', b)
    freq = re.search(r'Final Frequency\s*:\s*([\d\.]+)\s*Hz', b)
    est = re.search(r'Estimator Mode\s*:\s*(\w+)', b)
    conf = re.search(r'Confidence\s*:\s*([\d\.]+)%', b)
    
    # Top 5 spectral peaks
    peaks = re.findall(r'#(\d):\s*Bin\s*(\d+)\s*\|\s*Raw:\s*([\d\.]+)\s*Hz.*?Mag:\s*([\d\.]+)\s*\|\s*Floor:\s*([\d\.]+)\s*\|\s*Prom:\s*([\d\.]+)x\s*\|\s*SNR:\s*([\+\-\d\.]+)\s*dB', b)
    
    # Selected hyp
    best_hyp = re.search(r'Best Hyp Freq\s*:\s*([\d\.]+)\s*Hz', b)
    
    # E2 candidate
    e2_cand = re.search(r'\[E2 CANDIDATE\]:\s*Freq:\s*([\d\.]+)\s*Hz.*?Raw:\s*([\d\.]+)\s*\|\s*Final:\s*([\d\.]+)\s*\|\s*H_Count:\s*(\d)\s*\|\s*Mask:\s*(0x[0-9A-Fa-f]+)\s*\|\s*Penalties:\s*(.*?)\n', b)
    
    # E2 harmonics m=1..4
    m_matches = re.findall(r'm=(\d):\s*Target k=\s*(\d+)\s*\|\s*Peak bin=\s*(\d+)\s*\(\s*([\d\.]+)\s*Hz\).*?f0/\d=\s*([\d\.]+)\s*Hz\s*\|\s*Mag=\s*([\d\.]+)\s*\|\s*Floor=\s*([\d\.]+)\s*\|\s*Prom=\s*([\d\.]+)x\s*\(SNR\s*([\+\-\d\.]+)dB\)\s*\|\s*LP:\s*(\w+)\s*\|\s*PassGate:\s*(\w+)', b)
    
    # E3 candidate
    e3_cand = re.search(r'\[E3 CANDIDATE\]:\s*Freq:\s*([\d\.]+)\s*Hz.*?Raw:\s*([\d\.]+)\s*\|\s*Final:\s*([\d\.]+)\s*\|\s*H_Count:\s*(\d)\s*\|\s*Mask:\s*(0x[0-9A-Fa-f]+)\s*\|\s*Penalties:\s*(.*?)\n', b)
    
    results.append({
        'frame': f_num,
        'rms': float(rms.group(1)) if rms else 0.0,
        'state': state.group(1) if state else 'UNKNOWN',
        'note': note.group(1) if note else 'N/A',
        'freq': float(freq.group(1)) if freq else 0.0,
        'est': est.group(1) if est else 'INVALID',
        'conf': float(conf.group(1)) if conf else 0.0,
        'best_hyp': float(best_hyp.group(1)) if best_hyp else 0.0,
        'peaks': peaks,
        'e2_cand': e2_cand.groups() if e2_cand else None,
        'm_matches': m_matches,
        'e3_cand': e3_cand.groups() if e3_cand else None
    })

print(f'Total parsed: {len(results)}')
active = [r for r in results if r['rms'] >= 0.015 and len(r['m_matches']) > 0]
print(f'Active acoustic frames with E2 candidate: {len(active)}')

for idx, a in enumerate(active[:15]):
    top_p = a['peaks'][0] if a['peaks'] else ('1', '0', '0', '0', '0', '0', '0')
    f_num = a['frame']
    st = a['state']
    nt = a['note']
    fq = a['freq']
    rm = a['rms']
    cf = a['conf']
    es = a['est']
    print(f"\n--- FRAME #{f_num} | State: {st} | Note: {nt} | Freq: {fq:.2f} Hz | RMS: {rm:.4f} | Conf: {cf:.1f}% | Est: {es} ---")
    print(f"  Strongest Peak: Bin {top_p[1]} ({top_p[2]} Hz, Mag: {top_p[3]}, Floor: {top_p[4]}, Prom: {top_p[5]}x)")
    for m in a['m_matches']:
        m_idx, tgt_k, pk_b, pk_f, f0_div, mag, flr, prm, snr, lp, gate = m
        print(f"    m={m_idx}: f={pk_f}Hz (Bin {pk_b}) | f0/{m_idx}={f0_div}Hz | Mag={mag} | Floor={flr} | Prom={prm}x ({snr}dB) | LP={lp} | Gate={gate}")
    if a['e2_cand']:
        c_f, c_raw, c_fin, c_cnt, c_msk, c_pen = a['e2_cand']
        print(f"  E2 Score -> Raw: {c_raw} | Final: {c_fin} | H_Count: {c_cnt} (Mask: {c_msk}) | Penalties: {c_pen}")
    if a['e3_cand']:
        c_f, c_raw, c_fin, c_cnt, c_msk, c_pen = a['e3_cand']
        print(f"  E3 Score -> Raw: {c_raw} | Final: {c_fin} | H_Count: {c_cnt} (Mask: {c_msk}) | Penalties: {c_pen}")
