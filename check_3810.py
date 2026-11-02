import json

transcript_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript.jsonl'
with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 3825 <= idx <= 4050:
            d = json.loads(line)
            if d.get('type') == 'USER_INPUT':
                print(f"User input at {idx}: {d.get('content', '')[:120]}")
            elif d.get('tool_calls'):
                for tc in d['tool_calls']:
                    desc = str(tc.get('args', {}).get('Description', ''))
                    cmd = str(tc.get('args', {}).get('CommandLine', ''))
                    tf = str(tc.get('args', {}).get('TargetFile', ''))
                    if desc or cmd or tf:
                        print(f"Tool {idx}: {desc[:40]} | {cmd[:40]} | {tf[:40]}")
