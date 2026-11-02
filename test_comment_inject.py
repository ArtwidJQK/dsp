# -*- coding: utf-8 -*-
"""
Test creating and verifying Word comments in python-docx
"""

import zipfile
import docx
from lxml import etree as ET

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CT_NS = "http://schemas.openxmlformats.org/package/2006/content-types"
NSMAP = {'w': W_NS}

doc = docx.Document()
p = doc.add_paragraph()
r1 = p.add_run("Van ban binh thuong. ")
r2 = p.add_run("[CAN BO SUNG]")
r3 = p.add_run(" Tiep tuc van ban.")
doc.save("test_comment_target.docx")

# Function to inject comments
def inject_comments_into_docx(docx_path, comments_list):
    # comments_list: list of dict(id=0, text="...", search_str="[CAN BO SUNG]")
    zin_path = docx_path + ".tmp"
    import shutil
    shutil.copy2(docx_path, zin_path)
    
    with zipfile.ZipFile(zin_path, 'r') as zin, zipfile.ZipFile(docx_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == '[Content_Types].xml':
                root = ET.fromstring(data)
                # check if override exists
                override_exists = False
                for child in root:
                    if child.get('PartName') == '/word/comments.xml':
                        override_exists = True
                if not override_exists:
                    new_override = ET.SubElement(root, f'{{{CT_NS}}}Override')
                    new_override.set('PartName', '/word/comments.xml')
                    new_override.set('ContentType', 'application/vnd.openxmlformats-officedocument.wordprocessingml.comments+xml')
                data = ET.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                
            elif item.filename == 'word/_rels/document.xml.rels':
                root = ET.fromstring(data)
                rel_exists = False
                max_rid = 0
                for child in root:
                    rid_str = child.get('Id', '')
                    if rid_str.startswith('rId'):
                        try:
                            max_rid = max(max_rid, int(rid_str[3:]))
                        except:
                            pass
                    if child.get('Target') == 'comments.xml':
                        rel_exists = True
                if not rel_exists:
                    new_rel = ET.SubElement(root, f'{{{REL_NS}}}Relationship')
                    new_rel.set('Id', f'rId{max_rid + 1}')
                    new_rel.set('Type', 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/comments')
                    new_rel.set('Target', 'comments.xml')
                data = ET.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                
            elif item.filename == 'word/document.xml':
                root = ET.fromstring(data)
                # search for runs matching comments
                for c_item in comments_list:
                    cid = str(c_item['id'])
                    target_txt = c_item['target']
                    # Find w:r with target_txt
                    for r in root.xpath('.//w:r', namespaces=NSMAP):
                        t_nodes = r.xpath('.//w:t', namespaces=NSMAP)
                        if t_nodes and target_txt in "".join([t.text for t in t_nodes if t.text]):
                            # Add commentRangeStart before r, commentRangeEnd after r, commentReference
                            parent_p = r.getparent()
                            idx = parent_p.index(r)
                            
                            range_start = ET.Element(f'{{{W_NS}}}commentRangeStart')
                            range_start.set(f'{{{W_NS}}}id', cid)
                            
                            range_end = ET.Element(f'{{{W_NS}}}commentRangeEnd')
                            range_end.set(f'{{{W_NS}}}id', cid)
                            
                            ref_run = ET.Element(f'{{{W_NS}}}r')
                            ref_rpr = ET.SubElement(ref_run, f'{{{W_NS}}}rPr')
                            ref_style = ET.SubElement(ref_rpr, f'{{{W_NS}}}rStyle')
                            ref_style.set(f'{{{W_NS}}}val', 'CommentReference')
                            ref_elem = ET.SubElement(ref_run, f'{{{W_NS}}}commentReference')
                            ref_elem.set(f'{{{W_NS}}}id', cid)
                            
                            parent_p.insert(idx, range_start)
                            parent_p.insert(idx + 2, range_end)
                            parent_p.insert(idx + 3, ref_run)
                            break
                            
                data = ET.tostring(root, xml_declaration=True, encoding='UTF-8', standalone=True)
                
            zout.writestr(item, data)
            
        # Write word/comments.xml
        c_root = ET.Element(f'{{{W_NS}}}comments', nsmap={'w': W_NS})
        for c_item in comments_list:
            cid = str(c_item['id'])
            c_elem = ET.SubElement(c_root, f'{{{W_NS}}}comment')
            c_elem.set(f'{{{W_NS}}}id', cid)
            c_elem.set(f'{{{W_NS}}}author', c_item.get('author', 'Biên tập viên kỹ thuật'))
            c_elem.set(f'{{{W_NS}}}date', '2026-10-06T14:00:00Z')
            c_elem.set(f'{{{W_NS}}}initials', 'BTV')
            
            p_elem = ET.SubElement(c_elem, f'{{{W_NS}}}p')
            p_pr = ET.SubElement(p_elem, f'{{{W_NS}}}pPr')
            p_style = ET.SubElement(p_pr, f'{{{W_NS}}}pStyle')
            p_style.set(f'{{{W_NS}}}val', 'CommentText')
            
            r_ref = ET.SubElement(p_elem, f'{{{W_NS}}}r')
            r_rpr = ET.SubElement(r_ref, f'{{{W_NS}}}rPr')
            r_style = ET.SubElement(r_rpr, f'{{{W_NS}}}rStyle')
            r_style.set(f'{{{W_NS}}}val', 'CommentReference')
            ET.SubElement(r_ref, f'{{{W_NS}}}annotationRef')
            
            r_text = ET.SubElement(p_elem, f'{{{W_NS}}}r')
            t_elem = ET.SubElement(r_text, f'{{{W_NS}}}t')
            t_elem.text = c_item['text']
            
        c_data = ET.tostring(c_root, xml_declaration=True, encoding='UTF-8', standalone=True)
        zout.writestr('word/comments.xml', c_data)
        
    import os
    os.remove(zin_path)
    print("Injected comments successfully!")

# Run test
inject_comments_into_docx("test_comment_target.docx", [
    {'id': 0, 'target': '[CAN BO SUNG]', 'text': 'Ghi chú biên tập: Tác giả cần bổ sung thông tin này.'}
])

# Test opening with docx
d_check = docx.Document("test_comment_target.docx")
print("Verified! Target docx opened cleanly with comments. Paragraphs:", len(d_check.paragraphs))
