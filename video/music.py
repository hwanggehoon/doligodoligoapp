"""Original ambient score for the promo video (synthesized, royalty-free by construction).

80 BPM, 4/4 → one bar = 3.0 s. Chords change every 2 bars (6 s) so scene cuts land on
chord changes. Layers: warm pad, soft piano arpeggio, sub bass, shimmer bells,
ocean-wave bed, two gentle swells. Output: 48 kHz 16-bit stereo WAV.

  python3 video/music.py [out.wav] [seconds]
"""
import math
import sys
import wave

import numpy as np
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
BAR = 3.0
EIGHTH = BAR / 8

CHORDS = {  # MIDI voicings
    "Dmaj9": [50, 57, 61, 64, 66],
    "Bm9":   [47, 54, 57, 61, 62],
    "Gmaj9": [43, 50, 54, 57, 59],
    "A69":   [45, 52, 59, 61, 66],
    "F#m7":  [42, 49, 52, 57, 61],
    "Em9":   [40, 47, 50, 54, 55],
}
ROOT = {"Dmaj9": 38, "Bm9": 35, "Gmaj9": 31, "A69": 33, "F#m7": 30, "Em9": 28}
PROG = ["Dmaj9", "Bm9", "Gmaj9", "A69", "Dmaj9", "Bm9", "Gmaj9", "A69",
        "F#m7", "Bm9", "Em9", "Gmaj9", "A69", "Dmaj9"]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, "low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, "high", fs=SR, output="sos"), x)


def env_adsr(n, a, r, sustain_len):
    t = np.arange(n) / SR
    e = np.clip(t / a, 0, 1)
    rel_start = sustain_len
    e *= np.where(t > rel_start, np.clip(1 - (t - rel_start) / r, 0, 1), 1)
    return e ** 1.5


def pad_voice(freq, dur, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    for det in (-5, 0, 6):  # cents
        f = freq * 2 ** (det / 1200)
        ph = rng.uniform(0, 2 * math.pi)
        for k in range(1, 9):
            out += (1 / k ** 1.35) * np.sin(2 * math.pi * f * k * t + ph * k)
    lfo = 1 + 0.12 * np.sin(2 * math.pi * rng.uniform(0.08, 0.16) * t + rng.uniform(0, 6))
    return out * lfo / 6


def piano_note(freq, dur, vel, rng):
    n = int(dur * SR)
    t = np.arange(n) / SR
    out = np.zeros(n)
    B = 0.0004  # slight inharmonicity
    for k in range(1, 12):
        fk = freq * k * math.sqrt(1 + B * k * k)
        if fk > 12000:
            break
        amp = 1 / k ** 1.7
        decay = 0.9 / (1 + 0.35 * (k - 1)) * (220 / max(freq, 110)) ** 0.3
        out += amp * np.exp(-t / decay) * np.sin(2 * math.pi * fk * t + rng.uniform(0, 0.3))
    att = np.clip(t / 0.004, 0, 1)
    click = rng.normal(0, 1, n) * np.exp(-t / 0.004) * 0.02
    return (out * att + click) * vel


def bell(freq, dur, vel):
    n = int(dur * SR)
    t = np.arange(n) / SR
    partials = [(1, 1.0, 2.8), (2.76, 0.35, 1.2), (5.4, 0.18, 0.6), (8.93, 0.08, 0.35)]
    out = sum(a * np.exp(-t / d) * np.sin(2 * math.pi * freq * r * t) for r, a, d in partials)
    return out * np.clip(t / 0.003, 0, 1) * vel


def add(buf, sig, start, pan=0.0, gain=1.0):
    i = int(start * SR)
    if i >= buf.shape[1]:
        return
    j = min(buf.shape[1], i + len(sig))
    s = sig[: j - i] * gain
    l = math.cos((pan + 1) * math.pi / 4)
    r = math.sin((pan + 1) * math.pi / 4)
    buf[0, i:j] += s * l
    buf[1, i:j] += s * r


def reverb_ir(seconds, rng, decay=1.1):
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = np.zeros((2, n))
    for c in range(2):
        noise = rng.normal(0, 1, n)
        noise = lp(noise, 6000)
        ir[c] = noise * np.exp(-t / decay)
        ir[c, : int(0.012 * SR)] *= np.linspace(0, 1, int(0.012 * SR))
    return ir / np.abs(ir).max()


def render(total=84.0, seed=7):
    rng = np.random.default_rng(seed)
    n = int((total + 6) * SR)
    dry = np.zeros((2, n))
    pads = np.zeros((2, n))
    slot = 2 * BAR

    # --- pad
    for i, name in enumerate(PROG):
        start = i * slot
        dur = slot + 2.4
        for m in CHORDS[name]:
            v = pad_voice(hz(m), dur, rng) * env_adsr(int(dur * SR), 1.6, 2.2, slot)
            add(pads, v, start, pan=rng.uniform(-0.5, 0.5), gain=0.050)
    pads[0] = lp(pads[0], 1500)
    pads[1] = lp(pads[1], 1500)

    # --- piano arpeggio (from slot 1, sparser in intro and final)
    pattern = [0, 2, 1, 3, 2, 4, 3, 1]
    for i, name in enumerate(PROG):
        if i == 0:
            continue
        tones = sorted(m + 12 for m in CHORDS[name][1:])
        density = 0.45 if i < 3 else (0.8 if i < 13 else 0.35)
        for e in range(16):
            if rng.random() > density:
                continue
            m = tones[pattern[e % 8] % len(tones)]
            if e % 8 == 0 and rng.random() < 0.5:
                m += 12
            vel = rng.uniform(0.45, 0.8) * (1.0 if e % 4 == 0 else 0.75)
            add(dry, piano_note(hz(m), 3.2, vel, rng), i * slot + e * EIGHTH + rng.normal(0, 0.006),
                pan=(m - 66) / 30, gain=0.075)

    # --- sub bass (from slot 2)
    for i, name in enumerate(PROG):
        if i < 2:
            continue
        f = hz(ROOT[name])
        d = slot + 0.8
        t = np.arange(int(d * SR)) / SR
        b = (np.sin(2 * math.pi * f * t) + 0.18 * np.sin(4 * math.pi * f * t)) * env_adsr(len(t), 0.25, 0.8, slot)
        add(dry, b, i * slot, gain=0.085 if i < 13 else 0.06)

    # --- shimmer bells over the location + closing sections
    for i in (7, 8, 12, 13):
        tones = [m + 24 for m in CHORDS[PROG[i]][2:]]
        for k in range(4):
            if rng.random() < 0.8:
                add(dry, bell(hz(tones[k % len(tones)]), 4.0, rng.uniform(0.3, 0.5)),
                    i * slot + k * BAR / 2 + BAR * 0.25, pan=rng.uniform(-0.7, 0.7), gain=0.035)

    # --- swells into 42 s (locations) and 60 s (numbers)
    for hit in (42.0, 60.0):
        d = 2.5
        t = np.arange(int(d * SR)) / SR
        sw = lp(rng.normal(0, 1, len(t)), 2500) * (t / d) ** 3
        add(dry, sw, hit - d, gain=0.03)
        tb = np.arange(int(2.0 * SR)) / SR
        boom = np.sin(2 * math.pi * 52 * tb) * np.exp(-tb / 0.45)
        add(dry, boom, hit, gain=0.10)

    # --- ocean bed
    t = np.arange(n) / SR
    noise = rng.normal(0, 1, n)
    surf = lp(noise, 700) * (0.55 + 0.45 * np.sin(2 * math.pi * t / 7.3) ** 2)
    surf2 = hp(lp(rng.normal(0, 1, n), 3500), 900) * (0.5 + 0.5 * np.sin(2 * math.pi * t / 7.3 + 0.9) ** 4)
    bed_level = np.interp(t, [0, 6, 12, 72, 80, total + 6], [1.0, 0.9, 0.45, 0.4, 0.9, 0.8])
    bed = (surf * 0.020 + surf2 * 0.006) * bed_level
    dry[0] += bed
    dry[1] += np.roll(bed, 480)

    # --- reverb
    ir = reverb_ir(3.6, rng)
    mix_in = dry + pads
    wet = np.stack([fftconvolve(mix_in[c], ir[c])[:n] for c in range(2)]) * 0.10
    mix = mix_in * 0.85 + wet

    # --- master
    mix[0] = hp(mix[0], 32)
    mix[1] = hp(mix[1], 32)
    mix = mix[:, : int(total * SR)]
    tt = np.arange(mix.shape[1]) / SR
    fade = np.clip(tt / 1.5, 0, 1) * np.clip((total - tt) / 4.5, 0, 1)
    mix *= fade
    rms = np.sqrt(np.mean(mix ** 2))
    mix *= 10 ** (-18 / 20) / max(rms, 1e-9)
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    peak = np.abs(mix).max()
    if peak > 0.89:
        mix *= 0.89 / peak
    return mix


def write_wav(path, mix):
    pcm = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(pcm.tobytes())


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "video/music.wav"
    total = float(sys.argv[2]) if len(sys.argv) > 2 else 84.0
    m = render(total)
    write_wav(out, m)
    print(f"wrote {out}: {m.shape[1] / SR:.1f}s, peak {np.abs(m).max():.2f}, rms {20 * np.log10(np.sqrt(np.mean(m ** 2))):.1f} dBFS")
