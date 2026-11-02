import docx
import re
import zipfile
import lxml.etree as ET

ORIG_DOCX = r"D:\dsp\LeTanDung_24150654\LeTanDung_24150654.docx"
V2_DOCX   = r"D:\dsp\LeTanDung_24150654\LeTanDung_24150654_v2.docx"

print("=" * 60)
print("VERIFICATION OF TABLES 5.1, 5.2, 5.4, 5.5 DATA INTEGRITY")
print("=" * 60)

doc_orig = docx.Document(ORIG_DOCX)
doc_v2   = docx.Document(V2_DOCX)

def get_table_text_matrix(table):
    matrix = []
    for row in table.rows:
        row_txt = [c.text.strip().replace('\n', ' ') for c in row.cells]
        matrix.append(row_txt)
    return matrix

# Find tables in original docx
orig_tables = {}
for i, t in enumerate(doc_orig.tables):
    txt0 = t.rows[0].cells[0].text.strip()
    if "Target" in txt0 or "Nốt" in txt0:
        for r in t.rows:
            if "A4" in r.cells[0].text:
                if "440.000" in [c.text for c in r.cells]:
                    orig_tables["5.1"] = t
                if "Đợt 1" in [c.text for c in t.rows[0].cells] or "Run 1" in [c.text for c in t.rows[0].cells]:
                    orig_tables["5.2"] = t
                if "Đỉnh 1" in [c.text for c in t.rows[0].cells]:
                    orig_tables["5.4"] = t
                if "f₁ / f_max" in [c.text for c in t.rows[0].cells] or "f1 / fmax" in [c.text for c in t.rows[0].cells]:
                    orig_tables["5.5"] = t

v2_tables = {}
for i, t in enumerate(doc_v2.tables):
    hdrs = [c.text.strip() for c in t.rows[0].cells]
    if any("Mục tiêu" in h for h in hdrs) and any("Đo được" in h for h in hdrs):
        v2_tables["5.1"] = t
    elif any("Đợt 1" in h for h in hdrs) and any("Đợt 2" in h for h in hdrs):
        v2_tables["5.2"] = t
    elif any("Đỉnh 1" in h for h in hdrs):
        v2_tables["5.4"] = t
    elif any("f₁ / f_max" in h for h in hdrs):
        v2_tables["5.5"] = t

# Check Table 5.1
print("\n--- CHECKING TABLE 5.1 ---")
t51_notes = ["A4", "C4", "C5", "D3", "E3", "E2"]
for r in v2_tables["5.1"].rows[1:]:
    note = r.cells[0].text.strip()
    target = r.cells[1].text.strip()
    measured = r.cells[2].text.strip()
    dev = r.cells[3].text.strip()
    mae_hz = r.cells[4].text.strip()
    mae_c = r.cells[5].text.strip()
    max_err = r.cells[6].text.strip()
    std = r.cells[7].text.strip()
    valid = r.cells[8].text.strip()
    oct_err = r.cells[9].text.strip()
    estimator = r.cells[10].text.strip()
    print(f"[{note}] Target={target} Hz, Measured={measured} Hz, Dev={dev} Hz, MAE={mae_hz} Hz ({mae_c} c), MaxErr={max_err} Hz, Std={std} Hz, Valid={valid}, OctErr={oct_err}, Estimator={estimator}")

# Check Table 5.2
print("\n--- CHECKING TABLE 5.2 ---")
for r in v2_tables["5.2"].rows[1:]:
    note = r.cells[0].text.strip()
    run1 = r.cells[1].text.strip()
    run2 = r.cells[2].text.strip()
    dev1 = r.cells[3].text.strip()
    dev2 = r.cells[4].text.strip()
    diff = r.cells[5].text.strip()
    print(f"[{note}] Run1={run1}, Run2={run2}, Dev1={dev1}, Dev2={dev2}, Diff={diff}")

# Check Table 5.4
print("\n--- CHECKING TABLE 5.4 ---")
for r in v2_tables["5.4"].rows[1:]:
    note = r.cells[0].text.strip()
    p1 = r.cells[1].text.strip()
    p2 = r.cells[2].text.strip()
    p3 = r.cells[3].text.strip()
    p4 = r.cells[4].text.strip()
    p5 = r.cells[5].text.strip()
    print(f"[{note}] f1={p1} | f2={p2} | f3={p3} | f4={p4} | f5={p5}")

# Check Table 5.5
print("\n--- CHECKING TABLE 5.5 ---")
for r in v2_tables["5.5"].rows[1:]:
    note = r.cells[0].text.strip()
    r1 = r.cells[1].text.strip()
    r2 = r.cells[2].text.strip()
    r3 = r.cells[3].text.strip()
    r4 = r.cells[4].text.strip()
    r5 = r.cells[5].text.strip()
    print(f"[{note}] r1={r1} | r2={r2} | r3={r3} | r4={r4} | r5={r5}")

# Check Placeholders [CẦN BỔ SUNG...]
print("\n" + "=" * 60)
print("COUNTING [CẦN BỔ SUNG...] AND [CẦN GIẢI THÍCH...] IN V2")
print("=" * 60)
placeholders = []
for p in doc_v2.paragraphs:
    m = re.findall(r'\[CẦN\s+[^\]]+\]', p.text)
    if m:
        placeholders.extend(m)
for t in doc_v2.tables:
    for row in t.rows:
        for c in row.cells:
            m = re.findall(r'\[CẦN\s+[^\]]+\]', c.text)
            if m:
                placeholders.extend(m)

placeholders = list(set(placeholders))
for i, ph in enumerate(placeholders):
    print(f"{i+1}. {ph}")
print(f"Total unique placeholders: {len(placeholders)}")

# Check Word Comments in XML
print("\n" + "=" * 60)
print("INSPECTING WORD COMMENTS IN V2 ZIPFILE")
print("=" * 60)
with zipfile.ZipFile(V2_DOCX, 'r') as z:
    comments_xml = z.read('word/comments.xml')
    root = ET.fromstring(comments_xml)
    W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    comments = root.findall(f'.//{{{W_NS}}}comment')
    print(f"Total Word comments in comments.xml: {len(comments)}")
    for c in comments:
        cid = c.get(f'{{{W_NS}}}id')
        author = c.get(f'{{{W_NS}}}author')
        txt = ''.join([t.text for t in c.findall(f'.//{{{W_NS}}}t') if t.text])
        print(f"Comment #{cid} [{author}]: {txt}")
