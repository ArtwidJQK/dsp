import json

transcript_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript.jsonl'
full_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript_full.jsonl'

# Look at lines between 3300 and 3435
with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 3340 <= idx <= 3435:
            d = json.loads(line)
            tcs = d.get('tool_calls', [])
            for tc in tcs:
                name = tc.get('name') or tc.get('tool_name') or ''
                args = tc.get('args', {})
                tgt = args.get('TargetFile', '')
                if 'main.c' in tgt:
                    print(f"Line {idx}: {name} -> {args.get('Description', '')}")
