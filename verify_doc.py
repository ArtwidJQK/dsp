# -*- coding: utf-8 -*-
import docx

doc = docx.Document('LeTanDung_24150654.docx')
print('Total paragraphs:', len(doc.paragraphs))
print('Total tables:', len(doc.tables))

word_count = sum(len(p.text.split()) for p in doc.paragraphs)
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            word_count += sum(len(p.text.split()) for p in cell.paragraphs)

print('Total word count (approx):', word_count)

# Check headings
headings = [p.text for p in doc.paragraphs if p.text.startswith('CHƯƠNG') or p.text.startswith('TÀI') or p.text.startswith('PHỤ') or p.text.startswith('TÓM') or p.text.startswith('ABSTRACT') or p.text.startswith('MỤC') or p.text.startswith('DANH')]
print('\nMain Section Headings found:')
for h in headings:
    print(' -', h)

# Check tables
print(f'\nChecking all {len(doc.tables)} tables:')
for i, t in enumerate(doc.tables):
    rows = len(t.rows)
    cols = len(t.columns)
    first_cell = t.rows[0].cells[0].text[:40].strip().replace('\n', ' ')
    print(f' Table {i+1}: {rows} rows x {cols} cols | First cell: "{first_cell}"')

# Verify key data points
full_text = "\n".join([p.text for p in doc.paragraphs])
for t in doc.tables:
    for row in t.rows:
        for cell in row.cells:
            full_text += " " + cell.text

keys = [
    "440.281", "261.674", "523.438", "146.797", "164.787",
    "23.56", "25.37", "INMP441", "ESP32-S3", "GPIO 4", "GPIO 5", "GPIO 6",
    "REAL-DATA ONLY", "NOT VERIFIED", "E2"
]
print("\nData verification check:")
for k in keys:
    count = full_text.count(k)
    print(f' Key "{k}": found {count} times (PASS)' if count > 0 else f' Key "{k}": NOT FOUND (FAIL)')
