"""
Splits side-by-side composites where two phone photos sit inside a portrait frame
with blurred padding. Detects the inner photo bounding box per half via edge density.
"""
from PIL import Image, ImageFilter
import numpy as np
import os

BASE = r"f:\Alex_Workspace\ernst-haus-garten\public\images\referenzen"
QUALITY = 90

side_by_side = [
    "heckenschnitt-eingang.jpg",
    "gehoelzschnitt-vorher-nachher.jpg",
    "hofzufahrt-vorher-nachher.jpg",
]


def detect_photo_bbox(half_img: Image.Image) -> tuple[int, int, int, int]:
    """Find bounding box of the sharp (non-blurred) inner photo.

    Approach: per-pixel high-pass via |gray - blur(gray)|. Sharp photo regions
    yield high values; smooth blur padding yields ~0. Then per-row/col average,
    and threshold at 30% of peak.
    """
    gray = half_img.convert("L")
    blurred = gray.filter(ImageFilter.GaussianBlur(radius=4))
    g = np.array(gray, dtype=np.int16)
    b = np.array(blurred, dtype=np.int16)
    high = np.abs(g - b).astype(np.float32)

    h, w = high.shape
    row_energy = high.mean(axis=1)
    col_energy = high.mean(axis=0)

    # Smooth a bit so single noisy rows do not dominate
    def smooth(x: np.ndarray, k: int = 9) -> np.ndarray:
        kernel = np.ones(k) / k
        return np.convolve(x, kernel, mode="same")

    row_energy = smooth(row_energy)
    col_energy = smooth(col_energy)

    row_thresh = row_energy.max() * 0.30
    col_thresh = col_energy.max() * 0.30

    rows = np.where(row_energy > row_thresh)[0]
    cols = np.where(col_energy > col_thresh)[0]

    if len(rows) == 0 or len(cols) == 0:
        return (0, 0, w, h)

    top, bottom = int(rows.min()), int(rows.max())
    left, right = int(cols.min()), int(cols.max())

    margin = 2
    top = max(0, top - margin)
    left = max(0, left - margin)
    bottom = min(h, bottom + margin + 1)
    right = min(w, right + margin + 1)
    return (left, top, right, bottom)


def unified_crop(half: Image.Image, bbox: tuple[int, int, int, int],
                 target_w: int, target_h: int) -> Image.Image:
    """Crop the half so the photo is centered inside a (target_w, target_h) box."""
    hw, hh = half.size
    cx = (bbox[0] + bbox[2]) // 2
    cy = (bbox[1] + bbox[3]) // 2

    left = cx - target_w // 2
    top = cy - target_h // 2
    right = left + target_w
    bottom = top + target_h

    # Clamp inside the half (shift the window if needed)
    if left < 0:
        right -= left
        left = 0
    if top < 0:
        bottom -= top
        top = 0
    if right > hw:
        left -= (right - hw)
        right = hw
    if bottom > hh:
        top -= (bottom - hh)
        bottom = hh
    left = max(0, left)
    top = max(0, top)
    return half.crop((left, top, right, bottom))


for filename in side_by_side:
    src = os.path.join(BASE, filename)
    if not os.path.exists(src):
        print(f"  SKIP {filename}: nicht gefunden")
        continue
    img = Image.open(src).convert("RGB")
    w, h = img.size
    name = os.path.splitext(filename)[0]

    half_w = w // 2
    left_half = img.crop((0, 0, half_w, h))
    right_half = img.crop((half_w, 0, w, h))

    lb = detect_photo_bbox(left_half)
    rb = detect_photo_bbox(right_half)

    # Unified target dimensions: max of both bboxes so both photos fit in full
    target_w = max(lb[2] - lb[0], rb[2] - rb[0])
    target_h = max(lb[3] - lb[1], rb[3] - rb[1])
    # Cap to half dimensions
    target_w = min(target_w, half_w)
    target_h = min(target_h, h)

    vor = unified_crop(left_half, lb, target_w, target_h)
    nach = unified_crop(right_half, rb, target_w, target_h)

    vor_path = os.path.join(BASE, f"{name}-vor.jpg")
    nach_path = os.path.join(BASE, f"{name}-nach.jpg")
    vor.save(vor_path, "JPEG", quality=QUALITY, optimize=True)
    nach.save(nach_path, "JPEG", quality=QUALITY, optimize=True)

    print(f"  {filename} ({w}x{h})")
    print(f"    vor:  bbox={lb} -> {vor.size}")
    print(f"    nach: bbox={rb} -> {nach.size}")

print("Done.")
