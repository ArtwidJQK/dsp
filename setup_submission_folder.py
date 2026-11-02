# -*- coding: utf-8 -*-
"""
Setup submission folder: D:\dsp\LeTanDung_24150654
and D:\dsp\LeTanDung_24150654\sources
"""

import os
import shutil

BASE_SUBMISSION = r"D:\dsp\LeTanDung_24150654"
SOURCES_DIR = os.path.join(BASE_SUBMISSION, "sources")
BINARIES_DIR = os.path.join(SOURCES_DIR, "binaries")

os.makedirs(BASE_SUBMISSION, exist_ok=True)
os.makedirs(SOURCES_DIR, exist_ok=True)
os.makedirs(os.path.join(SOURCES_DIR, "main"), exist_ok=True)
os.makedirs(BINARIES_DIR, exist_ok=True)

print(f"Created directories:\n- {BASE_SUBMISSION}\n- {SOURCES_DIR}\n- {BINARIES_DIR}")

# 1. Copy LeTanDung_24150654.docx to BASE_SUBMISSION
src_docx = r"D:\dsp\artwid\piano_tuner\LeTanDung_24150654.docx"
dst_docx = os.path.join(BASE_SUBMISSION, "LeTanDung_24150654.docx")
if os.path.exists(src_docx):
    shutil.copy2(src_docx, dst_docx)
    print(f"Copied docx to: {dst_docx} ({os.path.getsize(dst_docx)} bytes)")
else:
    print(f"Warning: {src_docx} not found!")

# 2. Copy source files into sources/
shutil.copy2(r"D:\dsp\artwid\piano_tuner\CMakeLists.txt", os.path.join(SOURCES_DIR, "CMakeLists.txt"))
shutil.copy2(r"D:\dsp\artwid\piano_tuner\sdkconfig", os.path.join(SOURCES_DIR, "sdkconfig"))

shutil.copy2(r"D:\dsp\artwid\piano_tuner\main\CMakeLists.txt", os.path.join(SOURCES_DIR, "main", "CMakeLists.txt"))
shutil.copy2(r"D:\dsp\artwid\piano_tuner\main\main.c", os.path.join(SOURCES_DIR, "main", "main.c"))
shutil.copy2(r"D:\dsp\artwid\piano_tuner\main\index.html", os.path.join(SOURCES_DIR, "main", "index.html"))

# 3. Copy precompiled binaries into sources/binaries/
bin_src = r"D:\dsp\artwid\piano_tuner\build\piano_tuner.bin"
boot_src = r"D:\dsp\artwid\piano_tuner\build\bootloader\bootloader.bin"
part_src = r"D:\dsp\artwid\piano_tuner\build\partition_table\partition-table.bin"

if os.path.exists(bin_src):
    shutil.copy2(bin_src, os.path.join(BINARIES_DIR, "piano_tuner.bin"))
    print(f"Copied piano_tuner.bin ({os.path.getsize(bin_src)} bytes)")
if os.path.exists(boot_src):
    shutil.copy2(boot_src, os.path.join(BINARIES_DIR, "bootloader.bin"))
    print(f"Copied bootloader.bin ({os.path.getsize(boot_src)} bytes)")
if os.path.exists(part_src):
    shutil.copy2(part_src, os.path.join(BINARIES_DIR, "partition-table.bin"))
    print(f"Copied partition-table.bin ({os.path.getsize(part_src)} bytes)")

# 4. Copy helper scripts
for s in ["read_serial.py", "check_com3.py", "test_live_esp32_web.py"]:
    p = os.path.join(r"D:\dsp\artwid\piano_tuner", s)
    if os.path.exists(p):
        shutil.copy2(p, os.path.join(SOURCES_DIR, s))
        print(f"Copied {s}")

print("Setup submission folder completed.")
