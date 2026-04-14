"""
Batch-converts public/images/*.jpg to .webp.
- Max 1600px on longest edge (retina-safe for typical viewport)
- WebP quality 82 (visually lossless for photos)
- Keeps original filename (foo.jpg -> foo.webp)
- Leaves .jpg originals in place (delete separately after verifying refs)
"""
from PIL import Image
import os

BASE = r"f:\Alex_Workspace\ernst-haus-garten\public\images"
MAX_EDGE = 1600
QUALITY = 82

total_before = 0
total_after = 0
count = 0

for root, dirs, files in os.walk(BASE):
    for f in files:
        if not f.lower().endswith((".jpg", ".jpeg", ".png")):
            continue
        src = os.path.join(root, f)
        dst = os.path.join(root, os.path.splitext(f)[0] + ".webp")

        img = Image.open(src)
        if img.mode != "RGB":
            img = img.convert("RGB")

        w, h = img.size
        longest = max(w, h)
        if longest > MAX_EDGE:
            scale = MAX_EDGE / longest
            img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

        img.save(dst, "WEBP", quality=QUALITY, method=6)

        size_before = os.path.getsize(src)
        size_after = os.path.getsize(dst)
        total_before += size_before
        total_after += size_after
        count += 1

        pct = (1 - size_after / size_before) * 100
        rel = os.path.relpath(dst, BASE).replace("\\", "/")
        print(f"{size_before // 1024:>5}KB -> {size_after // 1024:>5}KB  ({pct:+5.0f}%)  {rel}")

print("---")
print(f"Files:  {count}")
print(f"Before: {total_before / 1024 / 1024:.2f} MB")
print(f"After:  {total_after / 1024 / 1024:.2f} MB")
print(f"Saved:  {(total_before - total_after) / 1024 / 1024:.2f} MB ({(1 - total_after / total_before) * 100:.0f}%)")
