"""Procedural 'atmosphere' backgrounds (blurred-photo look) for the deck and video.

These are not photographs. They are soft, out-of-focus scenes (night bokeh, sunset
over water, warm sauna light, pool caustics) used as backgrounds behind text and as
stand-ins in photo slots until real photography is dropped into assets/images/.

Usage:  python3 tools/atmos.py [out_dir]
"""
import math
import os
import sys

import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter, zoom

W, H = 1920, 1080


def hexrgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)], dtype=np.float32)


def to_linear(c):
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def to_srgb(c):
    c = np.clip(c, 0, None)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.power(c, 1 / 2.4) - 0.055)


def lin(h):
    return to_linear(hexrgb(h))


def vgradient(stops):
    """stops: list of (y_frac, hex). Returns HxWx3 linear image."""
    ys = np.linspace(0, 1, H, dtype=np.float32)
    out = np.zeros((H, 3), dtype=np.float32)
    pos = [s[0] for s in stops]
    cols = [lin(s[1]) for s in stops]
    for ch in range(3):
        out[:, ch] = np.interp(ys, pos, [c[ch] for c in cols])
    return np.repeat(out[:, None, :], W, axis=1)


def fractal_noise(rng, shape, octaves=5, base=8, persistence=0.55, stretch=(1, 1)):
    h, w = shape
    acc = np.zeros(shape, dtype=np.float32)
    amp, total = 1.0, 0.0
    for o in range(octaves):
        fh = max(2, int(base * (2 ** o) / stretch[0]))
        fw = max(2, int(base * (2 ** o) * (w / h) / stretch[1]))
        small = rng.random((fh, fw)).astype(np.float32)
        big = zoom(small, (h / fh, w / fw), order=3)[:h, :w]
        if big.shape != shape:
            big = np.pad(big, ((0, h - big.shape[0]), (0, w - big.shape[1])), mode="edge")
        acc += amp * big
        total += amp
        amp *= persistence
    acc /= total
    acc = (acc - acc.min()) / (acc.max() - acc.min() + 1e-6)
    return acc


def add_disc(img, cx, cy, r, color, intensity, rim=0.35, soft=1.6):
    """Additive bokeh disc with slightly brighter rim (lens-like)."""
    x0, x1 = int(max(0, cx - r - 4)), int(min(W, cx + r + 5))
    y0, y1 = int(max(0, cy - r - 4)), int(min(H, cy + r + 5))
    if x0 >= x1 or y0 >= y1:
        return
    yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    inside = np.clip((r - d) / soft + 0.5, 0, 1)
    prof = (1 - rim) + rim * np.clip(d / max(r, 1), 0, 1) ** 4
    a = inside * prof * intensity
    img[y0:y1, x0:x1] += a[..., None] * color[None, None, :]


def glow(img, sigma, strength):
    lum = img.copy()
    for ch in range(3):
        lum[..., ch] = gaussian_filter(img[..., ch], sigma)
    return img + lum * strength


def blur(img, sigma):
    out = np.empty_like(img)
    for ch in range(3):
        out[..., ch] = gaussian_filter(img[..., ch], sigma)
    return out


def finish(img, rng, exposure=1.0, grain=0.010, vignette=0.35, warmth=0.0):
    img = img * exposure
    # gentle filmic shoulder
    img = img / (1 + 0.35 * img)
    if warmth:
        img[..., 0] *= 1 + warmth
        img[..., 2] *= 1 - warmth
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
    img *= (1 - vignette * np.clip(r - 0.35, 0, None) ** 1.6)[..., None]
    out = to_srgb(img)
    out += rng.normal(0, grain, out.shape[:2]).astype(np.float32)[..., None]
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))


# ---------------------------------------------------------------- scenes

def night_harbor(seed=3, water=True, horizon=0.60, tint="#FFB45A"):
    """Out-of-focus city/harbor lights at night (Nampo-dong / Haeundae)."""
    rng = np.random.default_rng(seed)
    img = vgradient([(0, "#070D18"), (0.35, "#0E1B2E"), (horizon, "#2A2F4A"),
                     (horizon + 0.02, "#151C2C"), (1, "#060A12")])
    yy = np.arange(H, dtype=np.float32)[:, None]
    band = np.exp(-((yy - horizon * H) / (0.05 * H)) ** 2)
    img += band[..., None] * lin(tint)[None, None, :] * 0.10
    palette = [("#FFB45A", 5), ("#FFD08A", 4), ("#FF8A3D", 2), ("#FFF1DC", 3),
               ("#8FD3FF", 1.5), ("#5E9BFF", 1), ("#FF6FA8", 0.6)]
    names, weights = zip(*palette)
    weights = np.array(weights) / sum(weights)
    lights = np.zeros_like(img)
    n = 420
    for _ in range(n):
        y = rng.normal(horizon * H - 40, 0.075 * H)
        if rng.random() < 0.18:
            y = rng.uniform(0.15 * H, horizon * H)
        x = rng.uniform(-40, W + 40)
        r = float(np.clip(rng.lognormal(math.log(16), 0.55), 5, 80))
        col = lin(names[rng.choice(len(names), p=weights)])
        inten = rng.uniform(0.05, 0.28) * (1.3 if r < 12 else 1.0)
        add_disc(lights, x, y, r, col, inten)
        if water and y < horizon * H:
            ry = horizon * H + (horizon * H - y) * 0.55 + rng.normal(0, 6)
            if ry < H:
                for k in range(3):
                    add_disc(lights, x + rng.normal(0, 3), ry + k * r * 0.5, r * 0.8,
                             col, inten * 0.22 / (k + 1), rim=0.1, soft=4)
    lights = blur(lights, 1.2)
    img += lights
    if water:
        n2 = fractal_noise(rng, (H, W), octaves=4, base=6, stretch=(1, 6))
        wmask = np.clip((yy - horizon * H) / (0.05 * H), 0, 1)
        img *= (1 - 0.18 * wmask * n2)[..., None]
    img = glow(img, 26, 0.35)
    return finish(img, rng, exposure=1.25, vignette=0.45)


def sunset_estuary(seed=11, horizon=0.60):
    """Sunset over the Nakdong estuary: warm sky, glowing sun, water, reeds."""
    rng = np.random.default_rng(seed)
    img = vgradient([(0, "#2E3E66"), (0.22, "#56607F"), (0.42, "#C4807A"),
                     (horizon - 0.03, "#F2B36B"), (horizon, "#F6C98A"),
                     (horizon + 0.01, "#6C5B67"), (1, "#1E1B26")])
    sx, sy = 0.64 * W, (horizon - 0.035) * H
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt((xx - sx) ** 2 + ((yy - sy) * 1.15) ** 2)
    img += (np.exp(-(d / 260) ** 2) * 0.55)[..., None] * lin("#FFB870")[None, None, :]
    img += (np.exp(-(d / 70) ** 2) * 1.2)[..., None] * lin("#FFE7B8")[None, None, :]
    img += np.clip((34 - d) / 2, 0, 1)[..., None] * lin("#FFF4D8")[None, None, :] * 1.5
    # thin cloud streaks
    cl = fractal_noise(rng, (H, W), octaves=5, base=5, stretch=(1, 10))
    cl = np.clip((cl - 0.55) * 3, 0, 1) * np.clip(1 - np.abs(yy / H - 0.33) / 0.2, 0, 1)
    img = img * (1 - 0.35 * cl[..., None]) + cl[..., None] * lin("#F3A07E")[None, None, :] * 0.25
    # far shore: low hills + new-town towers (hazy)
    shore = np.zeros(W, dtype=np.float32)
    base_y = horizon * H
    x = 0
    while x < W:
        w = int(rng.uniform(18, 60))
        h = rng.uniform(4, 18)
        if 0.05 * W < x < 0.40 * W and rng.random() < 0.55:
            h = rng.uniform(30, 95)
        shore[x:x + w] = h
        x += w + int(rng.uniform(0, 12))
    shore = gaussian_filter(shore, 1.2)
    mask = (yy > (base_y - shore[None, :])) & (yy < base_y + 2)
    img[mask] = img[mask] * 0.35 + lin("#5B4A5E") * 0.35
    # water with sun reflection column broken by ripples
    wm = yy > base_y + 2
    rip = fractal_noise(rng, (H, W), octaves=4, base=8, stretch=(1, 14))
    col = np.exp(-((xx - sx) / 120) ** 2) * np.clip(1 - (yy - base_y) / (0.45 * H), 0, 1)
    refl = col * np.clip((rip - 0.45) * 3.0, 0, 1)
    img[wm] += (refl[wm] * 1.1)[:, None] * lin("#FFD39A")[None, :]
    img[wm] *= (0.85 + 0.25 * rip[wm])[:, None]
    # foreground reeds: thin stalks + feathery plumes, backlit by the sun
    reeds = np.zeros((H, W), dtype=np.float32)
    plumes = np.zeros((H, W), dtype=np.float32)
    for _ in range(170):
        x0 = rng.uniform(-50, W + 50)
        top = rng.uniform(0.66 * H, 0.90 * H)
        lean = rng.normal(0, 0.10)
        thick = 1 if rng.random() < 0.6 else 2
        ys = np.arange(int(top), H)
        xs = x0 + lean * (ys - top) + 5 * np.sin((ys - top) / 110)
        for yv, xv in zip(ys, xs):
            xi = int(xv)
            if 0 <= xi < W:
                reeds[yv, max(0, xi - thick):xi + thick] = 1
        # drooping plume made of many soft specks
        droop = rng.choice([-1, 1]) * rng.uniform(0.3, 0.9)
        plen = rng.uniform(40, 90)
        for t in np.linspace(0, 1, 60):
            px = x0 + droop * plen * t * 0.8 + rng.normal(0, 3.5 * t + 1)
            py = top - plen * (1 - t) * 0.35 + plen * t * 0.25 * abs(droop) + rng.normal(0, 3)
            xi, yi = int(px), int(py)
            if 0 <= xi < W - 2 and 0 <= yi < H - 2:
                plumes[yi:yi + 2, xi:xi + 2] += 0.7
    reeds = np.clip(gaussian_filter(reeds, 1.6) * 1.6, 0, 1)
    plumes = np.clip(gaussian_filter(plumes, 2.6) * 1.8, 0, 1)
    sun_near = np.exp(-(((xx - sx) / 520) ** 2 + ((yy - sy) / 420) ** 2))
    img = img * (1 - 0.62 * plumes[..., None]) + plumes[..., None] * (
        lin("#4A3530")[None, None, :] * 0.5 + sun_near[..., None] * lin("#FFC98A")[None, None, :] * 0.55)
    img = img * (1 - 0.88 * reeds[..., None]) + reeds[..., None] * lin("#2A1C1A")[None, None, :] * 0.5
    img = glow(img, 30, 0.25)
    return finish(img, rng, exposure=1.05, vignette=0.40, grain=0.009)


def ocean_skyline(seed=21, horizon=0.58):
    """Dusk sea with a tower skyline and a lit suspension bridge (Haeundae/Gwangalli mood)."""
    rng = np.random.default_rng(seed)
    img = vgradient([(0, "#16203F"), (0.30, "#34416B"), (0.48, "#8C6E8C"),
                     (horizon, "#E7A77E"), (horizon + 0.005, "#39405E"), (1, "#0D1222")])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    base_y = horizon * H
    # skyline towers on the right third
    sky = np.zeros((H, W), dtype=np.float32)
    windows = []
    x = int(0.60 * W)
    heights = [180, 240, 330, 420, 460, 400, 300, 360, 250, 210, 170, 280, 190]
    for i, hgt in enumerate(heights):
        w = int(rng.uniform(34, 62))
        top = base_y - hgt * rng.uniform(0.85, 1.1)
        sky[int(top):int(base_y), x:x + w] = 1
        for _ in range(int(hgt / 7)):
            windows.append((x + rng.uniform(4, w - 4), rng.uniform(top + 8, base_y - 6)))
        x += w + int(rng.uniform(4, 22))
        if x > W:
            break
    sky = gaussian_filter(sky, 2.2)
    img = img * (1 - 0.85 * sky[..., None]) + sky[..., None] * lin("#1B2036")[None, None, :] * 0.6
    lights = np.zeros_like(img)
    for (wx, wy) in windows:
        if rng.random() < 0.7:
            add_disc(lights, wx, wy, rng.uniform(2.5, 5), lin("#FFD9A0"), rng.uniform(0.25, 0.7), rim=0, soft=1.5)
    # suspension bridge across the left/middle
    deck_y = base_y - 38
    bx0, bx1 = -40, int(0.63 * W)
    towers = [int(0.18 * W), int(0.44 * W)]
    brg = np.zeros((H, W), dtype=np.float32)
    brg[int(deck_y):int(deck_y) + 5, max(0, bx0):bx1] = 1
    for tx in towers:
        brg[int(deck_y) - 170:int(deck_y) + 5, tx - 4:tx + 4] = 1
    spans = [(bx0, towers[0]), (towers[0], towers[1]), (towers[1], bx1)]
    for a, b in spans:
        xsp = np.arange(max(0, a), min(W, b))
        t = (xsp - a) / max(1, (b - a))
        ya = deck_y - (170 if a in towers else 10)
        yb = deck_y - (170 if b in towers else 10)
        sag = 150 if (a in towers and b in towers) else 70
        ycab = ya + (yb - ya) * t + sag * 4 * t * (1 - t) * 0.9
        for xv, yv in zip(xsp, ycab):
            brg[int(yv):int(yv) + 2, xv] = 1
        for xv, yv in zip(xsp[::9], ycab[::9]):
            add_disc(lights, xv, yv, 3.0, lin("#9FD8FF"), 0.55, rim=0, soft=1.2)
    for xv in range(max(0, bx0), bx1, 11):
        add_disc(lights, xv, deck_y + 2, 3.2, lin("#FFE2B0"), 0.7, rim=0, soft=1.2)
    brg = gaussian_filter(brg, 1.3)
    img = img * (1 - 0.8 * brg[..., None]) + brg[..., None] * lin("#141A2C")[None, None, :] * 0.4
    lights = blur(lights, 1.0)
    img += lights
    # sea texture + reflections: mirror the lights about the horizon, smear vertically
    rip = fractal_noise(rng, (H, W), octaves=4, base=8, stretch=(1, 16))
    wm = (yy > base_y + 1).astype(np.float32)
    lum = lights.sum(-1)
    mir = np.zeros_like(lum)
    hy = int(base_y)
    span = min(hy, H - hy - 1)
    mir[hy + 1:hy + 1 + span] = lum[hy - 1:hy - 1 - span:-1] if hy - 1 - span >= 0 else lum[hy - 1::-1][:span]
    mir = np.clip(mir - 0.12, 0, None)  # only the brighter lights reflect visibly
    fade = np.clip(1 - (yy - base_y) / (0.30 * H), 0, 1) ** 1.5
    mir = gaussian_filter(mir, (16, 1.2)) * np.clip((rip - 0.35) * 2.2, 0, 1) * fade
    img += (mir * wm * 0.9)[..., None] * lin("#FFD7A0")[None, None, :]
    img *= (1 - wm * (0.25 - 0.3 * rip * 0.5))[..., None]
    img = blur(img, 1.6)
    img = glow(img, 22, 0.4)
    return finish(img, rng, exposure=1.2, vignette=0.42)


def warm_sauna(seed=31):
    """Defocused wooden slats, warm lamps and steam."""
    rng = np.random.default_rng(seed)
    img = vgradient([(0, "#1A0F09"), (0.5, "#3A2213"), (1, "#140C07")])
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    slat = 0.5 + 0.5 * np.sin(xx / 46 * 2 * math.pi + 0.3 * np.sin(yy / 300))
    grain_n = fractal_noise(rng, (H, W), octaves=4, base=10, stretch=(12, 1))
    wood = (0.55 + 0.45 * slat) * (0.8 + 0.4 * grain_n)
    img *= wood[..., None]
    img += (np.exp(-(((xx - 0.30 * W) / 520) ** 2 + ((yy - 0.18 * H) / 300) ** 2)) * 0.6)[..., None] * lin("#FFB05C")
    img += (np.exp(-(((xx - 0.78 * W) / 420) ** 2 + ((yy - 0.30 * H) / 260) ** 2)) * 0.4)[..., None] * lin("#FF9C4A")
    lights = np.zeros_like(img)
    for _ in range(70):
        add_disc(lights, rng.uniform(0, W), rng.normal(0.80 * H, 0.08 * H), rng.uniform(10, 46),
                 lin(["#FFC47A", "#FFDDA8", "#FF9F55"][rng.integers(3)]), rng.uniform(0.06, 0.2))
    img += blur(lights, 1.5)
    steam = fractal_noise(rng, (H, W), octaves=5, base=3)
    img = img * (1 - 0.25 * steam[..., None]) + steam[..., None] * lin("#E8C7A2") * 0.12
    img = blur(img, 2.5)
    img = glow(img, 40, 0.3)
    return finish(img, rng, exposure=1.1, vignette=0.5, grain=0.011)


def _worley_edges(rng, n_points, warp=18.0):
    from scipy.spatial import cKDTree
    pts = rng.random((n_points, 2)) * [H, W]
    # replicate points around the frame so cells continue past the edges
    tiles = [pts + [dy, dx] for dy in (-H, 0, H) for dx in (-W, 0, W)]
    tree = cKDTree(np.concatenate(tiles))
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    wy = fractal_noise(rng, (H, W), octaves=3, base=4) - 0.5
    wx = fractal_noise(rng, (H, W), octaves=3, base=4) - 0.5
    q = np.stack([(yy + wy * warp * 2).ravel(), (xx + wx * warp * 2).ravel()], 1)
    d, _ = tree.query(q, k=2, workers=-1)
    return (d[:, 1] - d[:, 0]).reshape(H, W).astype(np.float32)


def pool_caustics(seed=41, dusk=True):
    """Turquoise pool water with caustic light network and a warm dusk glow (6F pool)."""
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    e1 = _worley_edges(rng, 260, warp=22)
    e2 = _worley_edges(rng, 900, warp=10)
    c = np.exp(-e1 / 5.0) * 0.9 + np.exp(-e2 / 3.2) * 0.45
    c = gaussian_filter(c, 1.1)
    depth = vgradient([(0, "#0E4F63"), (0.55, "#127189"), (1, "#0A3F52")])
    img = depth * (0.85 + 0.25 * fractal_noise(rng, (H, W), octaves=3, base=3)[..., None])
    img += c[..., None] * lin("#B8FFF6")[None, None, :] * 0.42
    if dusk:
        img += (np.exp(-(((xx - 0.82 * W) / 760) ** 2 + ((yy + 0.05 * H) / 520) ** 2)) * 0.32)[..., None] * lin("#FFB273")
    img = blur(img, 1.4)
    img = glow(img, 16, 0.22)
    return finish(img, rng, exposure=1.05, vignette=0.45, grain=0.008)


def paper_texture(seed=51, tone="#F7F3EC"):
    """Subtle warm paper fiber texture for light slides."""
    rng = np.random.default_rng(seed)
    n = fractal_noise(rng, (H, W), octaves=6, base=40, persistence=0.6)
    fib = fractal_noise(rng, (H, W), octaves=3, base=80, stretch=(1, 8))
    base = hexrgb(tone)
    img = np.ones((H, W, 3), dtype=np.float32) * base[None, None, :]
    img *= (0.985 + 0.02 * n + 0.008 * fib)[..., None]
    return Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))


SCENES = {
    "atmos_nampo_night": lambda: night_harbor(seed=3, water=True, horizon=0.58),
    "atmos_city_bokeh": lambda: night_harbor(seed=8, water=False, horizon=0.66, tint="#FF9A4A"),
    "atmos_haeundae_dusk": lambda: ocean_skyline(seed=21),
    "atmos_myeongji_sunset": lambda: sunset_estuary(seed=11),
    "atmos_sauna_warm": lambda: warm_sauna(seed=31),
    "atmos_pool_dusk": lambda: pool_caustics(seed=41),
    "paper": lambda: paper_texture(),
}

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "assets/atmos"
    only = sys.argv[2:] or list(SCENES)
    os.makedirs(out, exist_ok=True)
    for name in only:
        im = SCENES[name]()
        path = os.path.join(out, name + ".jpg")
        im.save(path, quality=90, subsampling=0, optimize=True)
        print("wrote", path)
