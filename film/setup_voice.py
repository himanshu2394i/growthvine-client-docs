"""Install the film voice (Kokoro, runs offline and free) in one step. Safe to run again: it skips what is done.

    python film/setup_voice.py            # installs into <tools>/growthvine-voice, then speaks a test line

<tools> is GV_TOOLS, or a `tools` folder beside the skill folder. Needs Python 3.10 to 3.12 for the voice's own
environment (found as `py -3.12` on Windows, or python3.12 / python3.11 / python3.10 elsewhere) and about 400 MB
of space. Downloads two model files (about 350 MB) from the kokoro-onnx release on GitHub.
"""
import os
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOOLS = Path(os.environ.get("GV_TOOLS", HERE.parents[1] / "tools"))
HOME = Path(os.environ.get("GV_VOICE_HOME", TOOLS / "growthvine-voice"))
BASE = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/"
FILES = [("kokoro-v1.0.onnx", BASE + "kokoro-v1.0.onnx", 325_532_387),
         ("voices-v1.0.bin", BASE + "voices-v1.0.bin", 28_214_398)]
VENV_PY = HOME / "venv" / ("Scripts/python.exe" if os.name == "nt" else "bin/python")


def find_python():
    """A Python the voice packages support (3.10 to 3.12)."""
    tries = [["py", "-3.12"], ["py", "-3.11"], ["py", "-3.10"]] if os.name == "nt" else []
    tries += [["python3.12"], ["python3.11"], ["python3.10"], [sys.executable]]
    for cmd in tries:
        if not shutil.which(cmd[0]):
            continue
        r = subprocess.run(cmd + ["-c", "import sys; print(sys.version_info[:2] >= (3, 10) and sys.version_info[:2] <= (3, 12))"],
                           capture_output=True, text=True)
        if r.returncode == 0 and r.stdout.strip() == "True":
            return cmd
    raise SystemExit("Need Python 3.10, 3.11 or 3.12 for the voice. Install Python 3.12 from python.org, then run this again.")


def main():
    HOME.mkdir(parents=True, exist_ok=True)
    tmp = TOOLS / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ, TMP=str(tmp), TEMP=str(tmp), PIP_CACHE_DIR=str(TOOLS / "pip-cache"))
    if not VENV_PY.exists():
        print("Creating the voice environment...")
        subprocess.run(find_python() + ["-m", "venv", str(HOME / "venv")], check=True, env=env)
    print("Installing kokoro-onnx and soundfile...")
    subprocess.run([str(VENV_PY), "-m", "pip", "install", "-q", "--disable-pip-version-check", "kokoro-onnx", "soundfile"], check=True, env=env)
    for name, url, size in FILES:
        p = HOME / name
        if p.exists() and p.stat().st_size == size:
            continue
        print(f"Downloading {name} ({size / 1e6:.0f} MB)...")
        part = p.with_suffix(p.suffix + ".part")
        urllib.request.urlretrieve(url, part)
        if part.stat().st_size != size:
            part.unlink()
            raise SystemExit(f"{name} downloaded at the wrong size; run this again.")
        part.replace(p)
    test = (f"from kokoro_onnx import Kokoro; import soundfile as sf; "
            f"k = Kokoro(r'{HOME / FILES[0][0]}', r'{HOME / FILES[1][0]}'); "
            f"a, sr = k.create('This is the Growthvine film voice.', voice='af_heart', speed=0.95, lang='en-us'); "
            f"sf.write(r'{HOME / 'test.wav'}', a, sr); print(round(len(a) / sr, 1))")
    secs = subprocess.run([str(VENV_PY), "-c", test], check=True, capture_output=True, text=True, env=env).stdout.strip()
    print(f"Voice ready at {HOME}. Test line: {HOME / 'test.wav'} ({secs} s).")


if __name__ == "__main__":
    main()
