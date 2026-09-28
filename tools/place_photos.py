"""Put supplied photos into the deck/video photo slots.

  python3 tools/place_photos.py path/to/image.png cover
  python3 tools/place_photos.py path/to/image.png loc_nampo --pos "40% 55%"
  python3 tools/place_photos.py --list            # show slots and which ones are filled

Each photo is converted to an sRGB JPEG (long edge <= 2560 px, EXIF/metadata stripped),
lightly upscaled when narrower than 1920 px, and saved as assets/images/<slot>.jpg.
--pos sets the crop focal point (CSS object-position) in assets/images/slots.json.
Then rebuild:  python3 deck/build.py  &&  python3 video/render.py
"""
import argparse
import json
import re
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps

ROOT = Path(__file__).resolve().parent.parent
IMAGES = ROOT / "assets" / "images"


def slot_names():
    src = (ROOT / "deck" / "data.js").read_text(encoding="utf-8")
    block = src[src.index("window.SLOTS"):]
    return re.findall(r"^\s+(\w+):\s+\{ fb:", block, flags=re.M)


def place(src, slot, pos=None):
    IMAGES.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    im = ImageOps.exif_transpose(im).convert("RGB")
    w, h = im.size
    if max(w, h) > 2560:
        s = 2560 / max(w, h)
        im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    elif w < 1920:
        s = 1920 / w
        im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
        im = im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=60, threshold=2))
    out = IMAGES / f"{slot}.jpg"
    im.save(out, quality=90, optimize=True, progressive=True)
    cfg_path = IMAGES / "slots.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8")) if cfg_path.exists() else {}
    if pos:
        cfg.setdefault(slot, {})["pos"] = pos
        cfg_path.write_text(json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{slot:15s} <- {Path(src).name}  ({im.size[0]}x{im.size[1]})  -> {out.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?")
    ap.add_argument("slot", nargs="?")
    ap.add_argument("--pos", default=None, help='focal point, e.g. "60% 45%"')
    ap.add_argument("--list", action="store_true")
    a = ap.parse_args()
    names = slot_names()
    if a.list or not a.src:
        have = {p.stem for p in IMAGES.glob("*.jpg")}
        for n in names:
            print(("[x] " if n in have else "[ ] ") + n)
        return
    if a.slot not in names:
        raise SystemExit(f"unknown slot '{a.slot}'. slots: {', '.join(names)}")
    place(a.src, a.slot, a.pos)


if __name__ == "__main__":
    main()
