"""
Re-encodes hero-garten.webp aggressively for LCP.
Target: ~120 KB at 1600x900.
Strategy: quality 70 with method=6 (slowest, best compression).
"""
from PIL import Image
import os

SRC_WEBP = r"f:\Alex_Workspace\ernst-haus-garten\public\images\hero-garten.webp"
DST = r"f:\Alex_Workspace\ernst-haus-garten\public\images\hero-garten.webp"

img = Image.open(SRC_WEBP)
if img.mode != "RGB":
    img = img.convert("RGB")

w, h = img.size
print(f"source: {w}x{h}, {os.path.getsize(SRC_WEBP) // 1024} KB")

for target_w in (1400, 1200, 1100):
    scale = target_w / w
    resized = img.resize((target_w, int(h * scale)), Image.LANCZOS)
    for q in (80, 75, 70):
        resized.save(DST, "WEBP", quality=q, method=6)
        size = os.path.getsize(DST)
        print(f"  {target_w}w q={q}: {size // 1024} KB")
        if size < 160 * 1024:
            print(f"  -> accepted ({resized.size}, {size // 1024} KB)")
            raise SystemExit

print("no target reached, final saved")
