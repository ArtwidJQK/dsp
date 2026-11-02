import json

full_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript_full.jsonl'

steps_to_extract = [4009, 4010, 4011, 4012, 4013, 4014]

with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if idx in steps_to_extract:
            d = json.loads(line)
            role = d.get('type') or d.get('source')
            content = d.get('content', '')
            print(f"=== STEP {idx} ({role}) ===")
            if isinstance(content, str):
                print(f"Content length: {len(content)}")
                # save to file
                with open(f'step_{idx}_output.txt', 'w', encoding='utf-8') as out_f:
                    out_f.write(content)
