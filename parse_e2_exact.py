import re

with open('real_piano_E2_10frames.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

blocks = text.split('==================== [E2-DIAG FRAME #')
print(f'Total frames in real_piano_E2_10frames.txt: {len(blocks)-1}')

frames_data = []
for b in blocks[1:]:
    f_num = b.split(']')[0]
    rms = re.search(r'RMS Energy Norm\s*:\s*([\d\.]+)', b)
    state = re.search(r'State:\s*(\w+)', b)
    note = re.search(r'Final Note\s*:\s*([A-G]#?\d|N/A)', b)
    freq = re.search(r'Final Frequency\s*:\s*([\d\.]+)\s*Hz', b)
    est = re.search(r'Estimator Mode\s*:\s*(\w+)', b)
    conf = re.search(r'Confidence\s*:\s*([\d\.]+)%', b)
    
    # Top spectral peak
    top_peak = re.search(r'#1:\s*Bin\s*(\d+)\s*\|\s*Raw:\s*([\d\.]+)\s*Hz.*?Mag:\s*([\d\.]+)\s*\|\s*Floor:\s*([\d\.]+)\s*\|\s*Prom:\s*([\d\.]+)x\s*\|\s*SNR:\s*([\+\-\d\.]+)\s*dB', b)
    
    # E2 candidate
    e2_cand = re.search(r'\[E2 CANDIDATE\]:.*?\n(.*?)(?=\[E3 CANDIDATE\]|>>> VERDICT|\n\s*\n)', b, re.DOTALL)
    
    e2_harms = {}
    if e2_cand:
        harm_lines = e2_cand.group(1).strip().split('\n')
        for hl in harm_lines:
            m_match = re.search(r'm=(\d):.*?Mag=\s*([\d\.]+).*?Floor=\s*([\d\.]+).*?Prom=\s*([\d\.]+)x.*?PassGate:(\w+)', hl)
            if m_match:
                e2_harms[int(m_match.group(1))] = {
                    'mag': float(m_match.group(2)),
                    'floor': float(m_match.group(3)),
                    'prom': float(m_match.group(4)),
                    'pass': m_match.group(5)
                }
                
    frames_data.append({
        'frame': f_num,
        'rms': float(rms.group(1)) if rms else 0.0,
        'state': state.group(1) if state else 'UNKNOWN',
        'note': note.group(1) if note else 'N/A',
        'freq': float(freq.group(1)) if freq else 0.0,
        'est': est.group(1) if est else 'INVALID',
        'conf': float(conf.group(1)) if conf else 0.0,
        'top_peak': top_peak.groups() if top_peak else None,
        'e2_harms': e2_harms
    })

print(f'Parsed {len(frames_data)} frames.')
for fd in frames_data[:10]:
    tp = fd['top_peak']
    tp_str = f"Bin {tp[0]} ({tp[1]}Hz, Mag {tp[2]})" if tp else "N/A"
    parts = []
    for m in range(1, 5):
        if m in fd['e2_harms']:
            h = fd['e2_harms'][m]
            parts.append(f"m={m}: mag={h['mag']:5.2f} (fl={h['floor']:4.2f}, pr={h['prom']:3.1f}x, {h['pass']})")
        else:
            parts.append(f"m={m}: N/A")
    h_str = " | ".join(parts)
    print(f"Frame #{fd['frame']:3s} | State: {fd['state']:11s} | Note: {fd['note']:4s} | Freq: {fd['freq']:7.2f}Hz | RMS: {fd['rms']:.4f} | Top: {tp_str}")
    print(f"   Harmonics -> {h_str}")
