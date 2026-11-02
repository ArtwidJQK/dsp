import json

full_path = r'C:\Users\dxem1\.gemini\antigravity-ide\brain\2897be21-3377-428f-8012-01a799ab0ede\.system_generated\logs\transcript_full.jsonl'

# Check step 4219 (output of view_file on index.html)
with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
    for idx, line in enumerate(f):
        if idx == 4219:
            d = json.loads(line)
            content = d.get('content', '')
            print(f"Step 4219 length: {len(content)}")
            # Let's save this content or check if it contains the full index.html
            with open('D:/Xử lý tín hiệu số/index_html_step4219.txt', 'w', encoding='utf-8') as out:
                out.write(content)
            print("Wrote index_html_step4219.txt")
            break
