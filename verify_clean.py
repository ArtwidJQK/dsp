import re

with open('step_3414_output.txt', 'r', encoding='utf-8') as f:
    lines_3414 = f.readlines()

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

print("Chunk 1 first 5 lines:")
for l in clean_3414[:5]:
    print(repr(l))

print("Chunk 2 first 5 lines:")
for l in clean_3416[:5]:
    print(repr(l))
