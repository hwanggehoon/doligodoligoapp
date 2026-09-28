"""Render video/promo.html frame-by-frame with headless Chromium and encode an MP4.

  python3 video/render.py                       # full video -> out/…홍보영상.mp4
  python3 video/render.py --stills 3,9,20,45    # QA stills -> out/stills/
  python3 video/render.py --start 40 --end 52 --out /tmp/part.mp4

The page exposes window.renderFrame(t); every frame is set explicitly, so the output is
deterministic (no reliance on real-time CSS animation).
"""
import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
# Chromium: $CHROME_PATH if set, else the cloud image's preinstalled build, else Playwright's own
# (run `python -m playwright install chromium` once on a local machine).
_CLOUD_CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
CHROME = os.environ.get("CHROME_PATH") or (_CLOUD_CHROME if os.path.exists(_CLOUD_CHROME) else None)
OUT_NAME = "C&C_프리미엄프라이빗커플스파_홍보영상.mp4"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=None)
    ap.add_argument("--out", type=str, default=str(ROOT / "out" / OUT_NAME))
    ap.add_argument("--stills", type=str, default="")
    ap.add_argument("--music", type=str, default=str(ROOT / "video" / "music.wav"))
    ap.add_argument("--crf", type=int, default=18)
    args = ap.parse_args()

    # make sure the deck's photo map is current (shared with the video)
    subprocess.run([sys.executable, str(ROOT / "deck" / "build.py"), "--no-pdf", "--no-png"], check=True,
                   stdout=subprocess.DEVNULL)

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=CHROME, args=["--allow-file-access-from-files"])
        page = browser.new_page(viewport={"width": 1920, "height": 1080})
        page.goto((ROOT / "video" / "promo.html").as_uri())
        page.wait_for_selector("body[data-ready='1']", timeout=60000)
        duration = page.evaluate("window.DURATION")
        end = args.end if args.end is not None else duration

        def frame(t):
            page.evaluate("t => new Promise(r => { renderFrame(t); requestAnimationFrame(() => r()); })", t)
            return page.screenshot(type="jpeg", quality=93, clip={"x": 0, "y": 0, "width": 1920, "height": 1080})

        if args.stills:
            d = ROOT / "out" / "stills"
            d.mkdir(parents=True, exist_ok=True)
            for t in [float(x) for x in args.stills.split(",") if x.strip()]:
                (d / f"t{t:06.2f}.jpg").write_bytes(frame(t))
            print("stills ->", d)
            browser.close()
            return

        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
               "-f", "image2pipe", "-framerate", str(args.fps), "-c:v", "mjpeg", "-i", "-"]
        if args.music and Path(args.music).exists():
            cmd += ["-ss", f"{args.start:.3f}", "-i", args.music]
        cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf), "-pix_fmt", "yuv420p",
                "-profile:v", "high", "-level", "4.1", "-r", str(args.fps)]
        if args.music and Path(args.music).exists():
            cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
        cmd += ["-movflags", "+faststart", args.out]
        enc = subprocess.Popen(cmd, stdin=subprocess.PIPE)

        n = int(round((end - args.start) * args.fps))
        t0 = time.time()
        for i in range(n):
            t = args.start + i / args.fps
            enc.stdin.write(frame(t))
            if i % 150 == 0:
                el = time.time() - t0
                print(f"frame {i}/{n}  t={t:5.1f}s  {el:5.0f}s elapsed", flush=True)
        enc.stdin.close()
        enc.wait()
        browser.close()
        print(f"video -> {args.out} ({Path(args.out).stat().st_size / 1e6:.1f} MB) in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
