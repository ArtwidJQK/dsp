import difflib

with open('main/main.c', 'r', encoding='utf-8') as f:
    mc = f.readlines()

with open('main/main_reverted.c', 'r', encoding='utf-8') as f:
    mr = f.readlines()

diff = list(difflib.unified_diff(mc, mr, fromfile='main.c', tofile='main_reverted.c'))
print(f"Diff lines: {len(diff)}")
for line in diff[:50]:
    print(line, end='')
