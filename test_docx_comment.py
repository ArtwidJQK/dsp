# -*- coding: utf-8 -*-
"""
Test Word comment injection into docx.
"""

import zipfile
import docx
from lxml import etree as ET

doc = docx.Document()
p = doc.add_paragraph('Day la van ban co comment.')
doc.save('test_comment.docx')

# Inspect XML
with zipfile.ZipFile('test_comment.docx', 'r') as zin:
    doc_xml = zin.read('word/document.xml').decode('utf-8')
    rels_xml = zin.read('word/_rels/document.xml.rels').decode('utf-8')
    content_types = zin.read('[Content_Types].xml').decode('utf-8')

print("Doc XML length:", len(doc_xml))
print("Rels XML has comments?:", 'comments' in rels_xml)
