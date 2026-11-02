import zipfile, os, shutil
from lxml import etree as ET

def clean_docx(docx_path):
    tmp_path = docx_path + '.clean.tmp'
    shutil.copy2(docx_path, tmp_path)

    with zipfile.ZipFile(tmp_path, 'r') as zin, zipfile.ZipFile(docx_path, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == 'docProps/thumbnail.':
                continue # remove orphaned thumbnail
            data = zin.read(item.filename)
            if item.filename == '_rels/.rels':
                root = ET.fromstring(data)
                for child in list(root):
                    if 'thumbnail' in child.get('Target', ''):
                        root.remove(child)
                data = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            zout.writestr(item, data)

    os.remove(tmp_path)
    print(f"Cleaned thumbnail from {docx_path}")

if __name__ == "__main__":
    clean_docx(r"D:\dsp\LeTanDung_24150654\LeTanDung_24150654_v2.docx")
