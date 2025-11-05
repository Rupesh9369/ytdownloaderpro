# build_win.py
import os, shutil, subprocess, sys

SCRIPT   = "ytprodownloaderpro.py"
ICON     = "icon.ico"
EXE_NAME = "YouTube Downloader Pro.exe"

# Clean
for p in ("dist", "build", EXE_NAME):
    if os.path.exists(p):
        if os.path.isdir(p):
            shutil.rmtree(p)
        else:
            os.remove(p)

cmd = [
    "pyinstaller",
    "--onefile",
    "--windowed",
    f"--icon={ICON}",
    f"--name=YouTube Downloader Pro",
    "--distpath=.",
    SCRIPT
]

print("Building Windows .exe...")
subprocess.run(cmd, check=True)
print(f"DONE! → {os.path.abspath(EXE_NAME)}")