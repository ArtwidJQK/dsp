import re

with open('verified_real_piano_E2.txt', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

raw_frames = text.split('==================== [E2-DIAG FRAME #')
print(f'Total DIAG frames: {len(raw_frames)-1}')

results = []
for rf in raw_frames[1:]:
    f_num = rf.split(']')[0]
    state_match = re.search(r'State:\s+([A-Z_]+)', rf)
    state = state_match.group(1) if state_match else ''
    
    rms_match = re.search(r'RMS Energy Norm\s+:\s+([\d\.]+)', rf)
    rms = float(rms_match.group(1)) if rms_match else 0.0
    
    note_match = re.search(r'Final Note\s+:\s+([A-G][b#]?\d)', rf)
    note = note_match.group(1) if note_match else 'N/A'
    
    freq_match = re.search(r'Final Frequency\s+:\s+([\d\.]+)\s+Hz', rf)
    freq = float(freq_match.group(1)) if freq_match else 0.0
    
    cents_match = re.search(r'Cents Error\s+:\s+([\+\-]?[\d\.]+)\s+cents', rf)
    cents = float(cents_match.group(1)) if cents_match else 0.0
    
    best_hyp = re.search(r'Best Hyp Freq\s+:\s+([\d\.]+)\s+Hz', rf)
    best_hyp_str = best_hyp.group(1) if best_hyp else ''
    
    est_match = re.search(r'Estimator Mode\s+:\s+([A-Z0-9_]+)', rf)
    est = est_match.group(1) if est_match else ''
    
    verdict_match = re.search(r'>>> VERDICT:\s+(.+)', rf)
    verdict = verdict_match.group(1).strip() if verdict_match else ''
    
    rank1_match = re.search(r'Rank # 1:\s+Cand\s+([\d\.]+)\s+Hz.*?Final:\s+([\d\.]+)', rf)
    rank1 = f'{rank1_match.group(1)}Hz (sc={rank1_match.group(2)})' if rank1_match else ''
    
    results.append({
        'frame': f_num, 'state': state, 'rms': rms, 'note': note, 'freq': freq,
        'cents': cents, 'best_hyp': best_hyp_str, 'est': est, 'verdict': verdict, 'rank1': rank1
    })

print(f'Total frames parsed: {len(results)}')
e2_frames = [r for r in results if r['note'] == 'E2']
e3_frames = [r for r in results if r['note'] == 'E3']
print(f'E2 recognized count: {len(e2_frames)} | E3 recognized count: {len(e3_frames)}')

for r in results:
    if r['note'] != 'N/A' or r['rms'] >= 0.025:
        line = f"Frame #{r['frame']:3s} | State: {r['state']:11s} | Note: {r['note']:4s} | Freq: {r['freq']:7.3f} Hz | Cents: {r['cents']:+5.2f} | Est: {r['est']:11s} | BestHyp: {r['best_hyp']:7s} | Rank1: {r['rank1']}"
        print(line)
        if r['verdict']:
            print(f"   >>> {r['verdict']}")
