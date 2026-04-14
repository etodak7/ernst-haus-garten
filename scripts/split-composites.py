"""
Splits Vorher/Nachher composite images into separate files.
- Vertical 2-stack composites: top half = vorher, bottom half = nachher
- 2x2 grid collage: 4 quadrants
"""
from PIL import Image
import os

BASE = r"f:\Alex_Workspace\ernst-haus-garten\public\images\referenzen"
QUALITY = 88

# Vertikal gestapelte Vorher/Nachher-Composites
vertical_2stack = [
    "heckenschnitt-strasse.jpg",
    "heckenschnitt-eingang.jpg",
    "heckenschnitt-herbst.jpg",
    "gartenpflege-teich.jpg",
    "hofflaeche-raeumung.jpg",
    "gehoelzschnitt-vorher-nachher.jpg",
    "hofzufahrt-vorher-nachher.jpg",
    "heckenschnitt-vorher-nachher.jpg",
    "gartenpflege-wildwuchs.jpg",
]

# 2x2 Grid Collage (4 verschiedene Szenen)
grid_2x2 = [
    "baumarbeiten-collage.jpg",
]

print("=== Vertikale 2-Stack splitten ===")
for filename in vertical_2stack:
    src = os.path.join(BASE, filename)
    if not os.path.exists(src):
        print(f"  SKIP {filename}: nicht gefunden")
        continue
    img = Image.open(src)
    w, h = img.size
    name = os.path.splitext(filename)[0]
    half = h // 2

    img.crop((0, 0, w, half)).save(
        os.path.join(BASE, f"{name}-vor.jpg"), "JPEG", quality=QUALITY, optimize=True
    )
    img.crop((0, half, w, h)).save(
        os.path.join(BASE, f"{name}-nach.jpg"), "JPEG", quality=QUALITY, optimize=True
    )
    print(f"  {filename} ({w}x{h}) -> -vor.jpg + -nach.jpg ({w}x{h-half})")

print()
print("=== 2x2 Grid splitten ===")
for filename in grid_2x2:
    src = os.path.join(BASE, filename)
    if not os.path.exists(src):
        print(f"  SKIP {filename}: nicht gefunden")
        continue
    img = Image.open(src)
    w, h = img.size
    name = os.path.splitext(filename)[0]
    hw, hh = w // 2, h // 2

    quadrants = {
        "tl": (0, 0, hw, hh),
        "tr": (hw, 0, w, hh),
        "bl": (0, hh, hw, h),
        "br": (hw, hh, w, h),
    }
    for tag, box in quadrants.items():
        img.crop(box).save(
            os.path.join(BASE, f"{name}-{tag}.jpg"), "JPEG", quality=QUALITY, optimize=True
        )
    print(f"  {filename} ({w}x{h}) -> 4 Quadranten ({hw}x{hh})")

print()
print("Done.")
