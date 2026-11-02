# Reconstruct the exact stable main.c by replacing ONLY the modified regions
# back to step 3414 and step 3416!

with open('main/main.c', 'r', encoding='utf-8') as f:
    current_content = f.read()

# Let's extract original calculate_local_noise_floor and evaluate_harmonic_hypothesis from step_3414_output.txt
with open('step_3414_output.txt', 'r', encoding='utf-8') as f:
    lines_3414 = f.readlines()

clean_3414 = []
for line in lines_3414[7:]:
    # format is: "line_num: code"
    if ':' in line:
        parts = line.split(':', 1)
        if parts[0].strip().isdigit():
            clean_3414.append(parts[1])

orig_chunk_1 = "".join(clean_3414)
print(f"Original chunk 1 length: {len(orig_chunk_1)} chars, {len(clean_3414)} lines")
print("First 3 lines of chunk 1:")
print("".join(clean_3414[:3]))
print("Last 3 lines of chunk 1:")
print("".join(clean_3414[-3:]))

# Let's extract original candidate loop & signal gate from step_3416_output.txt
with open('step_3416_output.txt', 'r', encoding='utf-8') as f:
    lines_3416 = f.readlines()

clean_3416 = []
for line in lines_3416[7:]:
    if ':' in line:
        parts = line.split(':', 1)
        if parts[0].strip().isdigit():
            clean_3416.append(parts[1])

orig_chunk_2 = "".join(clean_3416)
print(f"Original chunk 2 length: {len(orig_chunk_2)} chars, {len(clean_3416)} lines")
print("First 3 lines of chunk 2:")
print("".join(clean_3416[:3]))
print("Last 3 lines of chunk 2:")
print("".join(clean_3416[-3:]))
