"""
Generates og-default.jpg for social media previews.
1200x630 center-crop from hero-garten.jpg, ~85 quality, mozjpeg-style.
"""
from PIL import Image
import os

SRC = r"f:\Alex_Workspace\ernst-haus-garten\public\images\hero-garten.jpg"
DST = r"f:\Alex_Workspace\ernst-haus-garten\public\images\og-default.jpg"
TARGET_W, TARGET_H = 1200, 630

img = Image.open(SRC)
w, h = img.size
target_ratio = TARGET_W / TARGET_H
src_ratio = w / h

if src_ratio > target_ratio:
    new_w = int(h * target_ratio)
    left = (w - new_w) // 2
    crop = img.crop((left, 0, left + new_w, h))
else:
    new_h = int(w / target_ratio)
    top = (h - new_h) // 2
    crop = img.crop((0, top, w, top + new_h))

resized = crop.resize((TARGET_W, TARGET_H), Image.LANCZOS)
resized.save(DST, "JPEG", quality=85, optimize=True, progressive=True)

size_kb = os.path.getsize(DST) / 1024
print(f"og-default.jpg: {TARGET_W}x{TARGET_H}, {size_kb:.0f} KB")
