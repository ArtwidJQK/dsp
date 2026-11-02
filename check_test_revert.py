import json

transcript_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript.jsonl'
with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 3860 <= idx <= 3895:
            d = json.loads(line)
            if d.get('type') == 'PLANNER_RESPONSE':
                content = d.get('content', '')
                if content:
                    print(f"Plan {idx}: {content[:200]}\n")
