import json

full_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript_full.jsonl'

lines_to_inspect = [3433, 3437, 3441]
with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if idx in lines_to_inspect:
            d = json.loads(line)
            tcs = d.get('tool_calls', [])
            for tc in tcs:
                args = tc.get('args', {})
                print(f"=== STEP {idx} ===")
                print(f"Description: {args.get('Description')}")
                print(f"StartLine: {args.get('StartLine')}, EndLine: {args.get('EndLine')}")
                print("TargetContent:\n", args.get('TargetContent'))
                print("---")
