"""Box check: a padded box (a card) with a fixed height spills its text when a line wraps.
Cards hold text, so they take min-height; bars and shapes (no padding) may keep a fixed height.

    python film/gates/boxes.py <film_dir>      exit 1 when a card has a fixed height
"""
import re
import sys
from pathlib import Path

TAG = re.compile(r'<div\b([^>]*?)style=\\?"([^"\\]*)\\?"', re.S)
FIXED = re.compile(r'(?<![-\w])height\s*:\s*\d+px')


def check(film_dir):
    out = []
    for f in sorted((Path(film_dir) / "compositions").glob("*.html")):
        for m in TAG.finditer(f.read_text(encoding="utf-8")):
            attrs, style = m.group(1), m.group(2)
            if "padding" in style and FIXED.search(style):
                ident = re.search(r'(?:id|class)=\\?"([^"\\]+)', attrs)
                out.append(f"{f.stem}: {ident.group(1) if ident else 'card'} has a fixed height and padding; use min-height")
    return out


if __name__ == "__main__":
    found = check(sys.argv[1])
    print("\n".join(found) or "Boxes: no fixed-height cards.")
    sys.exit(1 if found else 0)
