import json

full_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript_full.jsonl'

with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if idx == 2933:
            d = json.loads(line)
            tcs = d.get('tool_calls', [])
            for tc in tcs:
                if 'index.html' in tc.get('args', {}).get('TargetFile', ''):
                    code = tc['args']['CodeContent']
                    with open('D:/Xử lý tín hiệu số/main/index.html_step2933', 'w', encoding='utf-8') as out:
                        out.write(code)
                    print(f"Extracted index.html from step 2933! Length: {len(code)}")
                    break
            break
