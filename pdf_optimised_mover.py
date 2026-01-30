# pdf_optimised_auto_move.py
# Location: E:/pdfhub/pdf/
# Run:      python E:/pdfhub/pdf/pdf_optimised_auto_move.py
#
# NO-UI, CUT/PASTE mover:
# - Source: parent folder (E:/pdfhub/)
# - Destination: this folder (E:/pdfhub/pdf/)  [repo root]
# - Moves ONLY PDFs containing "_optimised" (case-insensitive)
# - Skips if same filename already exists in destination
# - If name collision would happen, it will append " (1)", " (2)", ... and move anyway

from __future__ import annotations

import shutil
from pathlib import Path

KEYWORD = "_optimised"
DEST_DIR = Path(__file__).resolve().parent              # E:/pdfhub/pdf
SRC_DIR = DEST_DIR.parent                               # E:/pdfhub

def is_optimised_pdf(p: Path) -> bool:
    name_l = p.name.lower()
    return p.is_file() and name_l.endswith(".pdf") and (KEYWORD.lower() in name_l)

def safe_move(src: Path, dest_dir: Path) -> Path:
    """
    Move src into dest_dir.
    If dest exists, append (1), (2)... before extension.
    Returns the destination path used.
    """
    base = src.name
    name = src.stem
    ext = src.suffix

    target = dest_dir / base
    i = 1
    while target.exists():
        target = dest_dir / f"{name} ({i}){ext}"
        i += 1

    shutil.move(str(src), str(target))
    return target

def main():
    if not DEST_DIR.exists():
        DEST_DIR.mkdir(parents=True, exist_ok=True)

    dest_names = {p.name.lower() for p in DEST_DIR.iterdir() if p.is_file()}

    candidates = [p for p in SRC_DIR.iterdir() if is_optimised_pdf(p)]
    candidates.sort(key=lambda p: p.name.lower())

    if not candidates:
        print("No _optimised PDFs found in staging:", SRC_DIR)
        return

    moved = 0
    skipped = 0
    errors = 0

    for p in candidates:
        try:
            # Skip if exact same filename already present in destination
            if p.name.lower() in dest_names:
                skipped += 1
                continue

            dst = safe_move(p, DEST_DIR)
            moved += 1
            dest_names.add(dst.name.lower())
            print(f"MOVED: {p.name}  ->  {dst.name}")
        except Exception as e:
            errors += 1
            print(f"ERROR: {p.name}: {e}")

    print("\nSummary")
    print("-------")
    print(f"Moved:   {moved}")
    print(f"Skipped: {skipped} (same filename already in destination)")
    print(f"Errors:  {errors}")

if __name__ == "__main__":
    main()
