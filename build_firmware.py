import os
import subprocess
import sys

def main():
    env = os.environ.copy()
    idf_path = r"C:\ESP-IDF\v6.0.2\esp-idf"
    env["IDF_PATH"] = idf_path
    env["ESP_IDF_VERSION"] = "6.0.2"
    env["IDF_PYTHON_ENV_PATH"] = r"C:\Users\dxem1\.espressif\python_env\idf6.0_py3.14_env"
    
    extra_paths = [
        r"C:\Users\dxem1\.espressif\tools\xtensa-esp-elf\esp-15.2.0_20251204\xtensa-esp-elf\bin",
        r"C:\Users\dxem1\.espressif\tools\cmake\4.0.3\bin",
        r"C:\Users\dxem1\.espressif\tools\ninja\1.12.1",
        r"C:\Users\dxem1\.espressif\python_env\idf6.0_py3.14_env\Scripts",
        r"C:\Users\dxem1\.espressif\tools\idf-exe\1.0.3",
    ]
    env["PATH"] = os.pathsep.join(extra_paths) + os.pathsep + env.get("PATH", "")
    
    python_exe = r"C:\Users\dxem1\.espressif\python_env\idf6.0_py3.14_env\Scripts\python.exe"
    idf_py = os.path.join(idf_path, "tools", "idf.py")
    
    cmd = [python_exe, idf_py, "-C", r"D:\dsp\artwid\piano_tuner", "build"]
    print("Running:", " ".join(cmd))
    res = subprocess.run(cmd, env=env)
    if res.returncode != 0:
        print("Build failed with returncode:", res.returncode)
        sys.exit(res.returncode)
    print("Build successful!")

if __name__ == "__main__":
    main()
