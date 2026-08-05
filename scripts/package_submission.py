"""Nen CHI folder output/ thanh submission.zip - dung README goc muc 8-9 (KHONG kem source
code, .env, hay file audit nao khac). Chay scripts/validate_output.py TRUOC khi dung script nay.

Luu y: zip nay giu nguyen tien to "output/" ben trong (giai nen ra se duoc lai folder output/).
Neu form nop bai cua lop yeu cau file JSON nam thang o goc zip (khong co folder output/ bao
ngoai), doi dong arcname ben duoi tu f"output/{f.name}" thanh f.name.
"""
from __future__ import annotations

import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.config import OUTPUT_DIR, ROOT_DIR

ZIP_PATH = ROOT_DIR / "submission.zip"


def main() -> None:
    files = sorted(OUTPUT_DIR.glob("EC_*.json"))
    if len(files) != 50:
        print(f"CANH BAO: output/ dang co {len(files)}/50 file - chay scripts/validate_output.py truoc khi nop.")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in files:
            zf.write(f, arcname=f"output/{f.name}")

    print(f"Da tao {ZIP_PATH} voi {len(files)} file trong output/.")


if __name__ == "__main__":
    main()
