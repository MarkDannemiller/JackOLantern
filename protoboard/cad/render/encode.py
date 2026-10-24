"""Encode rendered frames to H.264 MP4 with burned-in captions (ffmpeg + libass).

    python3 cad/render/encode.py [name ...]      (default: every animation with frames)
Reads out/renders/frames/<name>/f_####.png, writes out/renders/<name>.mp4.
"""
import os
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUT = os.path.join(ROOT, "out", "renders")

TIER = {"a": "Tier A · Beginner", "b": "Tier B · Midrange", "c": "Tier C · Maxed"}
CAPTIONS = {
    **{f"explode-{t}": [(0.0, 2.2, f"Joyful Jack — {TIER[t]}"), (2.2, 5.2, "Every part pulls apart"),
                        (5.2, 8.2, "Base and pole · torso and costume · arms · head · hat"), (8.2, 12.0, "…and back together")] for t in "abc"},
    "walkthrough-b": [
        (0.0, 3.0, "Meet Joyful Jack — Tier B, the Midrange build"),
        (3.0, 8.2, "He waves at visitors his camera spots"),
        (8.6, 11.0, "Under the costume: an aluminium frame on a steel pole"),
        (11.0, 15.0, "Two Milwaukee M18 packs behind a back hatch — swap one while the other runs"),
        (15.0, 18.0, "Battery monitor, fuses and the emergency-stop relay"),
        (18.0, 21.0, "Power converters and the arm controllers"),
        (21.0, 25.0, "Each arm: seven smart motors that feel their own load"),
        (25.0, 28.0, "Glove hands that open and grip"),
        (28.0, 32.4, "The original head: eyes, eyelids, jaw, and a neck that turns and nods"),
        (32.6, 36.0, "Costume back on. Howdy!"),
    ],
}


def ts(t):
    h, rem = divmod(t, 3600)
    mnt, s = divmod(rem, 60)
    return f"{int(h)}:{int(mnt):02d}:{s:05.2f}"


def ass(name, path):
    lines = ["[Script Info]", "ScriptType: v4.00+", "PlayResX: 1280", "PlayResY: 720", "",
             "[V4+ Styles]",
             "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
             "Style: Cap,DejaVu Sans,30,&H00D6E6EF,&H000000FF,&H00101010,&H99101010,1,0,0,0,100,100,0.5,0,3,10,0,2,60,60,42,1",
             "", "[Events]", "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for a, b, text in CAPTIONS.get(name, []):
        lines.append(f"Dialogue: 0,{ts(a)},{ts(b)},Cap,,0,0,0,,{{\\fad(250,250)}}{text}")
    open(path, "w").write("\n".join(lines) + "\n")


def encode(name, fps=30):
    frames = os.path.join(OUT, "frames", name)
    sub = os.path.join(OUT, "frames", f"{name}.ass")
    ass(name, sub)
    out = os.path.join(OUT, f"{name}.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", os.path.join(frames, "f_%04d.png"),
           "-vf", f"ass={sub},format=yuv420p", "-c:v", "libx264", "-preset", "slow", "-crf", "22", "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    print(name, os.path.getsize(out) // 1024, "KiB")


if __name__ == "__main__":
    names = sys.argv[1:] or sorted(d for d in os.listdir(os.path.join(OUT, "frames")) if os.path.isdir(os.path.join(OUT, "frames", d)))
    for n in names:
        encode(n)
