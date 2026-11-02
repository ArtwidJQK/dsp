import difflib

with open('main/main.c', 'r', encoding='utf-8') as f:
    current = f.readlines()

with open('main/main_reverted.c', 'r', encoding='utf-8') as f:
    reverted = f.readlines()

diff = list(difflib.unified_diff(current, reverted, fromfile='main_current.c', tofile='main_reverted.c', n=3))
print(f"Total diff lines: {len(diff)}")
for line in diff[:120]:
    print(line, end='')
if len(diff) > 120:
    print(f"\n... and {len(diff)-120} more lines")
