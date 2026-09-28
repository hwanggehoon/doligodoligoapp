"""Render the landscape deck (deck/index.html) to PDF and PNG previews.

  python3 deck/build.py                 # final PDF (no photo-slot tags) + previews
  python3 deck/build.py --draft         # show tags on slots still using stand-in art
  python3 deck/build.py --no-pdf        # previews only

Photos: drop files named <slot>.jpg|jpeg|png|webp into assets/images/ (slot names are
listed in deck/data.js → SLOTS). Optional assets/images/slots.json can set a focal point
per slot, e.g. {"cover": {"pos": "65% 40%"}}.
"""
import argparse
import json
import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / "deck"
IMAGES = ROOT / "assets" / "images"
OUT = ROOT / "out"
# Chromium: $CHROME_PATH if set, else the cloud image's preinstalled build, else Playwright's own
# (run `python -m playwright install chromium` once on a local machine).
_CLOUD_CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
CHROME = os.environ.get("CHROME_PATH") or (_CLOUD_CHROME if os.path.exists(_CLOUD_CHROME) else None)
PDF_NAME = "C&C_프리미엄프라이빗커플스파_사업계획서_가로형.pdf"


def write_photo_map():
    cfg = {}
    cfg_path = IMAGES / "slots.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    photos = {}
    for p in sorted(IMAGES.glob("*")):
        if p.suffix.lower() not in (".jpg", ".jpeg", ".png", ".webp"):
            continue
        slot = p.stem
        entry = {"src": f"../assets/images/{p.name}"}
        if slot in cfg and "pos" in cfg[slot]:
            entry["pos"] = cfg[slot]["pos"]
        photos[slot] = entry
    # slots.json may also alias a slot to another file: {"closing": {"file": "cover.jpg"}}
    for slot, c in cfg.items():
        if "file" in c and (IMAGES / c["file"]).exists():
            photos[slot] = {"src": f"../assets/images/{c['file']}", **({"pos": c["pos"]} if "pos" in c else {})}
    (DECK / "photos.js").write_text("window.PHOTOS = " + json.dumps(photos, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    return photos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--draft", action="store_true", help="show tags on stand-in photo slots")
    ap.add_argument("--no-pdf", action="store_true")
    ap.add_argument("--no-png", action="store_true")
    ap.add_argument("--only", type=str, default="", help="comma list of 1-based slide numbers for PNGs")
    ap.add_argument("--scale", type=float, default=1.0, help="PNG device scale factor")
    args = ap.parse_args()

    photos = write_photo_map()
    print(f"photos found: {len(photos)} -> {', '.join(sorted(photos)) or '(none)'}")
    if args.no_pdf and args.no_png:  # only refresh deck/photos.js (used by video/render.py)
        return
    OUT.mkdir(exist_ok=True)
    prev = OUT / "preview"
    prev.mkdir(exist_ok=True)

    url = (DECK / "index.html").as_uri() + ("" if args.draft else "?tags=0")
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=["--allow-file-access-from-files"])  # CHROME=None -> Playwright's bundled Chromium
        page = browser.new_page(viewport={"width": 1920, "height": 1080}, device_scale_factor=args.scale)
        page.goto(url)
        page.wait_for_selector("body[data-ready='1']", timeout=60000)
        page.wait_for_timeout(300)
        slides = page.query_selector_all(".slide")
        print(f"slides: {len(slides)}")
        if not args.no_png:
            only = {int(x) for x in args.only.split(",") if x.strip()}
            for i, s in enumerate(slides, 1):
                if only and i not in only:
                    continue
                s.screenshot(path=str(prev / f"slide-{i:02d}.png"))
            print(f"previews -> {prev}")
        if not args.no_pdf:
            pdf_path = OUT / PDF_NAME
            page.emulate_media(media="print")
            page.pdf(path=str(pdf_path), width="1920px", height="1080px", print_background=True,
                     prefer_css_page_size=True)
            print(f"pdf -> {pdf_path} ({pdf_path.stat().st_size / 1e6:.1f} MB)")
        browser.close()

    if not args.no_pdf:
        import pymupdf  # set document metadata (pypdf's crypto import is broken on some images)
        path = OUT / PDF_NAME
        doc = pymupdf.open(path)
        doc.set_metadata({"title": "프리미엄 프라이빗 커플 스파 사업계획서 (가로형)", "author": "㈜C&C",
                          "subject": "사업계획서 · 영업 제안서", "creator": "deck/build.py"})
        doc.save(str(path) + ".tmp", garbage=3, deflate=True)
        doc.close()
        os.replace(str(path) + ".tmp", path)
        print(f"pdf metadata set ({path.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
