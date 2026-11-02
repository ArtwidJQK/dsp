import json

transcript_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript.jsonl'
full_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript_full.jsonl'

# Check step 4215 to 4235 in transcript.jsonl
with open(transcript_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if 4210 <= idx <= 4240:
            d = json.loads(line)
            t = d.get('type')
            content = d.get('content', '')
            tcs = d.get('tool_calls', [])
            print(f"Step {idx} [{t}]: {content[:60]}")
            for tc in tcs:
                print(f"   Tool: {tc.get('name') or tc.get('tool_name')}, args keys: {list(tc.get('args', {}).keys())}")
                if 'TargetFile' in tc.get('args', {}):
                    print(f"     TargetFile: {tc['args']['TargetFile']}")
                if 'CommandLine' in tc.get('args', {}):
                    print(f"     CommandLine: {tc['args']['CommandLine']}")
