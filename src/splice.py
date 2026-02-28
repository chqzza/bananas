import cv2
import numpy as np
import os

# === PATH TO YOUR SWORD SHEET ===
image_path = "assets/weapons/sword.png"  # change if needed

# Load with alpha
img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)

if img is None:
    raise FileNotFoundError(f"Couldn't load image: {image_path}")

if img.shape[2] < 4:
    raise ValueError("Image has no alpha channel — needs transparency")

# === ALPHA → MASK ===
alpha = img[:, :, 3]
_, thresh = cv2.threshold(alpha, 1, 255, cv2.THRESH_BINARY)

# === FIND CONTOURS ===
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Remove tiny junk contours
MIN_AREA = 50
filtered = [c for c in contours if cv2.contourArea(c) > MIN_AREA]

# Sort contours top-to-bottom, then left-to-right
boxes = [cv2.boundingRect(c) for c in filtered]
contours_sorted = [c for _, c in sorted(zip(boxes, filtered), key=lambda b: (b[0][1]//50, b[0][0]))]

# === OUTPUT ===
output_dir = "sprites"
os.makedirs(output_dir, exist_ok=True)

for i, cnt in enumerate(contours_sorted):
    x, y, w, h = cv2.boundingRect(cnt)
    sprite = img[y:y+h, x:x+w]

    # Trim extra transparent border (tight crop)
    alpha_crop = sprite[:, :, 3]
    coords = cv2.findNonZero(alpha_crop)
    x2, y2, w2, h2 = cv2.boundingRect(coords)
    sprite = sprite[y2:y2+h2, x2:x2+w2]

    cv2.imwrite(f"{output_dir}/sword_{i}.png", sprite)

print(f"Done. Extracted {len(contours_sorted)} sword sprites.")
