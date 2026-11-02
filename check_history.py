import json

transcript_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript.jsonl'

with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        d = json.loads(line)
        tcs = d.get('tool_calls', [])
        for tc in tcs:
            name = tc.get('name') or tc.get('tool_name') or ''
            args = tc.get('args', {})
            tf = args.get('TargetFile', '')
            if 'index.html' in tf or 'main.c' in tf:
                desc = args.get('Description', '')
                print(f"Line {idx}: {name} on {tf} -> {desc}")
