import json

full_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript_full.jsonl'

with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 3430 <= idx <= 3720:
            d = json.loads(line)
            tcs = d.get('tool_calls', [])
            for tc in tcs:
                name = tc.get('name') or tc.get('tool_name') or ''
                args = tc.get('args', {})
                tgt = args.get('TargetFile', '')
                if 'main.c' in tgt:
                    print(f"=== STEP {idx} ===")
                    print(f"Desc: {args.get('Description')}")
                    print(f"StartLine: {args.get('StartLine')}, EndLine: {args.get('EndLine')}")
                    tc_text = args.get('TargetContent', '')
                    rc_text = args.get('ReplacementContent', '')
                    print(f"Target len: {len(tc_text)}, Rep len: {len(rc_text)}")
