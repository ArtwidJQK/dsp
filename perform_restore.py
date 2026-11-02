import shutil
import os

print("Backing up current files...")
try:
    shutil.copyfile('main/index.html', 'main/index.html_upgraded_backup')
    shutil.copyfile('main/main.c', 'main/main_bassfix_backup.c')
except Exception as e:
    print("Backup note:", e)

print("Restoring index.html from step 2933...")
shutil.copyfile('main/index.html_step2933', 'main/index.html')

print("Restoring main.c from main_reverted.c...")
shutil.copyfile('main/main_reverted.c', 'main/main.c')

# Also sync to D:\dsp\LeTanDung_24150654\sources\main
sources_main = r"D:\dsp\LeTanDung_24150654\sources\main"
if os.path.exists(sources_main):
    print("Syncing to LeTanDung_24150654/sources/main...")
    try:
        shutil.copyfile('main/index.html', os.path.join(sources_main, 'index.html'))
        shutil.copyfile('main/main.c', os.path.join(sources_main, 'main.c'))
    except shutil.SameFileError:
        pass
    except Exception as e:
        print("Note on sources sync:", e)

print("Restoration complete!")
