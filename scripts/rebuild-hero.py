"""
Rebuilds hero-garten.webp from the original WhatsApp photo in alex/.
Single lossy encode (no cumulative quality loss).
"""
from PIL import Image
import os

SRC = r"f:\Alex_Workspace\alex\IMG-20250809-WA0000.jpeg"
DST = r"f:\Alex_Workspace\ernst-haus-garten\public\images\hero-garten.webp"
img = Image.open(SRC)
w, h = img.size
print(f"source: {w}x{h}, {os.path.getsize(SRC) // 1024} KB")

for target_w in (1400, 1200, 1100):
    scale = target_w / w
    resized = img.resize((target_w, int(h * scale)), Image.LANCZOS)
    for q in (78, 75, 72, 70):
        resized.save(DST, "WEBP", quality=q, method=6)
        size = os.path.getsize(DST)
        print(f"  {target_w}w q={q}: {size // 1024} KB")
        if size < 200 * 1024:
            break
    if size < 200 * 1024:
        break

print(f"final: {resized.size}, {os.path.getsize(DST) // 1024} KB")
