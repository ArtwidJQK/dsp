with open('step_3414_output.txt', 'r', encoding='utf-8') as f:
    lines_3414 = f.readlines()

import re
clean_3414 = []
for line in lines_3414[7:]:
    m = re.match(r'^\s*\d+:\s?(.*)', line)
    if m:
        clean_3414.append(m.group(1) + '\n')

with open('step_3416_output.txt', 'r', encoding='utf-8') as f:
    lines_3416 = f.readlines()

clean_3416 = []
for line in lines_3416[7:]:
    m = re.match(r'^\s*\d+:\s?(.*)', line)
    if m:
        clean_3416.append(m.group(1) + '\n')

with open('main/main.c', 'r', encoding='utf-8') as f:
    current_lines = f.readlines()

# Part A: lines before line 226 (0-indexed: 0..224)
part_A = current_lines[:224]

# Chunk 1: clean_3414 is lines 225..450 (which ends with line 444 before update_temporal_stability)
# Let's see what line update_temporal_stability is in clean_3414:
idx_temp = -1
for i, l in enumerate(clean_3414):
    if 'update_temporal_stability' in l:
        idx_temp = i
        break

print(f"clean_3414 total lines: {len(clean_3414)}, update_temporal_stability at index {idx_temp}")
# clean_3414[:idx_temp-2] is calculate_local_noise_floor and evaluate_harmonic_hypothesis
chunk_1_exact = clean_3414[:idx_temp-2] # up to return score; }

# Part B: from update_temporal_stability up to candidate_count = 0
idx_curr_temp = -1
idx_curr_cand = -1
for i, l in enumerate(current_lines):
    if 'static float update_temporal_stability' in l:
        idx_curr_temp = i
    if 'int candidate_count = 0;' in l:
        idx_curr_cand = i
        break

print(f"Current main.c: update_temporal_stability at line {idx_curr_temp+1}, candidate_count at line {idx_curr_cand+1}")
part_B = current_lines[idx_curr_temp-2:idx_curr_cand]

# Chunk 2: from candidate_count = 0 up to before // 9. Multi-Harmonic Weighted Quadratic Interpolation
idx_mhqi_clean = -1
for i, l in enumerate(clean_3416):
    if 'Multi-Harmonic Weighted Quadratic Interpolation' in l:
        idx_mhqi_clean = i
        break

print(f"clean_3416 total lines: {len(clean_3416)}, MHQI at index {idx_mhqi_clean}")
chunk_2_exact = clean_3416[:idx_mhqi_clean]

# Part C: from Multi-Harmonic Weighted Quadratic Interpolation to end of file
idx_curr_mhqi = -1
for i, l in enumerate(current_lines):
    if 'Multi-Harmonic Weighted Quadratic Interpolation' in l:
        idx_curr_mhqi = i
        break

print(f"Current main.c: MHQI at line {idx_curr_mhqi+1}")
part_C = current_lines[idx_curr_mhqi:]

reverted_lines = part_A + chunk_1_exact + part_B + chunk_2_exact + part_C

print(f"Total reverted lines: {len(reverted_lines)}")

with open('main/main_reverted.c', 'w', encoding='utf-8') as out_f:
    out_f.writelines(reverted_lines)

print("Saved to main/main_reverted.c successfully!")
