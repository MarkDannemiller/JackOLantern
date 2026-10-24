"""Copy the report's media into media/: the full-hardware renders (out/renders/mech) and the Protoboard diagrams as
web JPEGs, concept images, videos (renders and the Isaac Sim wave), and the merged build guides.

    python3 deliverables/2026-10-25-design-report/prepare_media.py
"""
import os
import shutil
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
R = os.path.join(PROJ, "protoboard", "out", "renders")
MEDIA = os.path.join(HERE, "media")
shutil.rmtree(MEDIA, ignore_errors=True)
os.makedirs(MEDIA, exist_ok=True)
RM = os.path.join(R, "mech")


def jpg(src, dst, width=1800, crop_bottom=0):
    im = Image.open(src).convert("RGB")
    if crop_bottom:
        im = im.crop((0, 0, im.width, im.height - crop_bottom))
    if im.width > width:
        im = im.resize((width, round(im.height * width / im.width)), Image.LANCZOS)
    im.save(os.path.join(MEDIA, dst), "JPEG", quality=84, optimize=True, progressive=True)


for f in sorted(os.listdir(RM)):
    if f.endswith(".png"):
        jpg(os.path.join(RM, f), f[:-4] + ".jpg", 2400 if f.startswith("lineup") else 1500)
    if f.endswith(".mp4"):
        shutil.copy(os.path.join(RM, f), os.path.join(MEDIA, f))
G = os.path.join(PROJ, "deliverables", "2026-10-25-build-guides")
for f in sorted(os.listdir(G)):
    if f.endswith(".pdf"):
        shutil.copy(os.path.join(G, f), os.path.join(MEDIA, f))
for f in os.listdir(os.path.join(R, "diagrams")):
    jpg(os.path.join(R, "diagrams", f), f[:-4] + ".jpg", 1800, crop_bottom=112)  # drops the viewer toolbar and its "server unreachable" toast
C = os.path.join(PROJ, "research", "concepts")
for src, dst in (("20261024-sketch-notebook.jpg", "concept-sketch.jpg"), ("20261024-head-real-build.jpg", "head-real.jpg"), ("20261024-concept-art-cowboy.jpg", "concept-art.jpg")):
    jpg(os.path.join(C, src), dst, 1000)
total = sum(os.path.getsize(os.path.join(MEDIA, f)) for f in os.listdir(MEDIA))
print(len(os.listdir(MEDIA)), "files", total // 1024 // 1024, "MiB")
