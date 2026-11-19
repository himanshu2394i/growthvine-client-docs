"""Set up Growthvine: everything the skill needs on this computer, in one run. Safe to run again.

    python setup_growthvine.py              # documents (PDF/PPT) and films
    python setup_growthvine.py --docs-only  # documents only

What it does:
  1. Checks Node 22+ and ffmpeg. They are normal programs the advisor installs once; if one is missing it prints the
     install command for this computer and carries on with the rest.
  2. Installs the document packages into this Python: reportlab (PDF), python-pptx (PPT), pymupdf (previews).
  3. Films: installs HyperFrames (pinned to the tested version) into <tools>/hyperframes, then the Chrome it renders
     with, then the Kokoro voice (film/setup_voice.py: about 350 MB, its own Python 3.10 to 3.12).
<tools> is GV_TOOLS, or a `tools` folder beside the skill folder. HyperFrames telemetry is off on every run.
"""
import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOOLS = Path(os.environ.get("GV_TOOLS", ROOT.parent / "tools"))
HYPERFRAMES = "0.9.58"
DOC_PACKAGES = ["reportlab", "python-pptx", "pymupdf"]
HINTS = {
    "node": {"win32": "winget install -e --id OpenJS.NodeJS.LTS",
             "darwin": "brew install node",
             "linux": "curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash - && sudo apt install -y nodejs"},
    "ffmpeg": {"win32": "winget install -e --id Gyan.FFmpeg",
               "darwin": "brew install ffmpeg",
               "linux": "sudo apt install -y ffmpeg"},
}


def node_ok(version):
    """Node 22 or newer ("v22.19.0")."""
    try:
        return int(version.strip().lstrip("v").split(".")[0]) >= 22
    except ValueError:
        return False


def missing(which, node_version):
    """System tools to install: 'node' (absent or older than 22; npm comes with it) and 'ffmpeg' (with ffprobe)."""
    out = []
    if not (which("node") and which("npm") and node_ok(node_version)):
        out.append("node")
    if not (which("ffmpeg") and which("ffprobe")):
        out.append("ffmpeg")
    return out


def hint(tool, platform=sys.platform):
    p = "win32" if platform.startswith("win") else "darwin" if platform == "darwin" else "linux"
    return HINTS[tool][p]


def node_version():
    node = shutil.which("node")
    if not node:
        return ""
    r = subprocess.run([node, "--version"], capture_output=True, text=True)
    return r.stdout.strip()


def env():
    tmp = TOOLS / "tmp"
    tmp.mkdir(parents=True, exist_ok=True)
    return dict(os.environ, HYPERFRAMES_NO_TELEMETRY="1", DO_NOT_TRACK="1", HYPERFRAMES_CACHE_DIR=str(TOOLS / "hf-cache"),
                npm_config_cache=str(TOOLS / "npm-cache"), PIP_CACHE_DIR=str(TOOLS / "pip-cache"), TMP=str(tmp), TEMP=str(tmp))


def docs():
    print("Document packages: " + ", ".join(DOC_PACKAGES) + "...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-q", "--disable-pip-version-check"] + DOC_PACKAGES,
                   check=True, env=env())


def hyperframes():
    home = TOOLS / "hyperframes"
    home.mkdir(parents=True, exist_ok=True)
    (home / ".npmrc").write_text(f"cache={TOOLS / 'npm-cache'}\n", encoding="utf-8")
    if not (home / "package.json").exists():
        (home / "package.json").write_text('{"name": "growthvine-tools", "private": true}\n', encoding="utf-8")
    print(f"HyperFrames {HYPERFRAMES}...")
    subprocess.run([shutil.which("npm"), "install", "--no-fund", "--no-audit", f"hyperframes@{HYPERFRAMES}"],
                   cwd=home, check=True, env=env())
    hf = home / "node_modules" / ".bin" / ("hyperframes.cmd" if os.name == "nt" else "hyperframes")
    print("Chrome for rendering...")
    subprocess.run([str(hf), "browser", "ensure"], cwd=home, check=True, env=env(), capture_output=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs-only", action="store_true")
    a = ap.parse_args()
    print(f"Setting up Growthvine. Tools folder: {TOOLS}")
    done, todo = [], []
    docs()
    done.append("documents (PDF, PPT)")
    if not a.docs_only:
        need = missing(shutil.which, node_version())
        for t in need:
            todo.append(f"{'Node 22+' if t == 'node' else 'ffmpeg'}: {hint(t)}")
        if "node" not in need:
            hyperframes()
            done.append(f"HyperFrames {HYPERFRAMES} and its Chrome")
        sys.path.insert(0, str(ROOT / "film"))
        import setup_voice
        setup_voice.main()
        done.append("film voice")
    print("\nReady: " + "; ".join(done))
    if todo:
        print("Still to install (then run this again):\n  " + "\n  ".join(todo))
        sys.exit(2)
    print("Growthvine is set up." + ("" if a.docs_only else " Films can be made on this computer."))


if __name__ == "__main__":
    main()
