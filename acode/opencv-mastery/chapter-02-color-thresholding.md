# Chapter 2: Color Spaces & Thresholding — "Is This Spot Empty?"

[← Chapter 1: Images](chapter-01-images.md) | [Chapter 3: Edge Detection →](chapter-03-edges.md)

---

## The Task

Raj: "Camera 3 sees 20 parking spots. I need a function that takes a frame and returns: spot 1 = empty, spot 2 = occupied, spot 3 = empty... You have until Friday."

---

## The Idea

An empty parking spot is gray asphalt. An occupied spot has a car on it — which is darker, more colorful, or has more texture than bare pavement.

The simplest approach: look at the pixels in each spot region. If they're mostly "asphalt-colored," it's empty. If they're something else, it's occupied.

But how do you define "asphalt-colored"?

---

## Grayscale Thresholding

The simplest form of segmentation: convert to grayscale, pick a cutoff value, and classify every pixel as black or white.

```python
import cv2
import numpy as np

img = cv2.imread("parking_lot.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Simple threshold: pixels > 127 become white (255), others become black (0)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

cv2.imshow("Original", gray)
cv2.imshow("Binary", binary)
cv2.waitKey(0)
```

`cv2.threshold(src, thresh, maxval, type)` returns:
- `_` → the threshold value used (useful for Otsu's method)
- `binary` → the output image (black and white only)

---

## Threshold Types

```python
# Pixels > thresh → white, else → black
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Pixels > thresh → black, else → white (inverted)
_, binary_inv = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY_INV)

# Pixels > thresh → thresh, else → unchanged
_, trunc = cv2.threshold(gray, 127, 255, cv2.THRESH_TRUNC)

# Pixels > thresh → unchanged, else → 0
_, tozero = cv2.threshold(gray, 127, 255, cv2.THRESH_TOZERO)
```

For parking detection, `THRESH_BINARY` is usually what you want.

---

## The Problem: What Threshold Value?

```python
# This works at noon (bright asphalt ≈ 160)
_, mask = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

# But at 5 PM (shadows, asphalt ≈ 90), everything is "occupied"
# And at night (asphalt ≈ 40), nothing works
```

A fixed threshold breaks when lighting changes. You need adaptive methods.

---

## Otsu's Method: Let the Image Decide

Otsu's method automatically finds the optimal threshold by analyzing the histogram:

```python
# Otsu's — automatically picks the best threshold
thresh_val, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

print(f"Otsu chose threshold: {thresh_val}")
```

Otsu assumes the image has two classes (foreground and background) and finds the value that best separates them. Works well when there's a clear bimodal distribution.

---

## Adaptive Thresholding: Handle Uneven Lighting

Real parking lots have shadows on one side and sun on the other. A single threshold can't handle both. Adaptive thresholding uses a different threshold for each region:

```python
# Adaptive threshold — calculates threshold for each small region
adaptive = cv2.adaptiveThreshold(
    gray,
    255,                              # max value
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,   # method (weighted mean of neighborhood)
    cv2.THRESH_BINARY,                # threshold type
    11,                               # block size (neighborhood size, must be odd)
    2                                 # C (constant subtracted from mean)
)
```

- `ADAPTIVE_THRESH_MEAN_C` — threshold = mean of neighborhood - C
- `ADAPTIVE_THRESH_GAUSSIAN_C` — threshold = weighted mean (Gaussian) - C
- Block size: larger = smoother, smaller = more detail
- C: larger = more pixels become white

---

## Color Spaces: Beyond Grayscale

Grayscale loses color information. A red car and gray asphalt might have the same brightness. Color spaces help:

### HSV (Hue, Saturation, Value)

```python
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# H: 0-179 (color/hue — red, green, blue...)
# S: 0-255 (saturation — gray to vivid)
# V: 0-255 (value/brightness — dark to bright)
```

HSV separates color (H) from brightness (V). This means you can detect "red cars" regardless of whether they're in sun or shadow.

### Why HSV for Parking Detection?

```python
# Asphalt characteristics in HSV:
# - Low saturation (it's gray, not colorful)
# - Medium value (not too dark, not too bright)

# Cars are typically:
# - Higher saturation (colored paint)
# - OR very different value (dark/bright compared to asphalt)

hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Mask for "low saturation" (gray-ish pixels = likely asphalt)
lower_gray = np.array([0, 0, 80])     # any hue, low sat, medium brightness
upper_gray = np.array([179, 50, 200]) # any hue, low sat, medium brightness

asphalt_mask = cv2.inRange(hsv, lower_gray, upper_gray)
```

---

## cv2.inRange: Color-Based Masking

`inRange` creates a binary mask where pixels within the specified range are white (255) and others are black (0):

```python
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# Detect blue cars
lower_blue = np.array([100, 50, 50])
upper_blue = np.array([130, 255, 255])
blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

# Detect red cars (red wraps around in HSV: 0-10 and 170-179)
lower_red1 = np.array([0, 50, 50])
upper_red1 = np.array([10, 255, 255])
lower_red2 = np.array([170, 50, 50])
upper_red2 = np.array([179, 255, 255])

red_mask = cv2.inRange(hsv, lower_red1, upper_red1) | cv2.inRange(hsv, lower_red2, upper_red2)
```

---

## The Parking Spot Detector (v1)

```python
import cv2
import numpy as np

def is_spot_occupied(frame, roi, empty_threshold=0.4):
    """
    Determine if a parking spot is occupied.
    
    Args:
        frame: Full camera frame (BGR)
        roi: Tuple (y1, y2, x1, x2) defining the spot region
        empty_threshold: Fraction of "non-asphalt" pixels to consider occupied
    
    Returns:
        bool: True if occupied, False if empty
    """
    y1, y2, x1, x2 = roi
    spot = frame[y1:y2, x1:x2]
    
    # Convert to HSV
    hsv = cv2.cvtColor(spot, cv2.COLOR_BGR2HSV)
    
    # Define "asphalt" range (low saturation, medium brightness)
    lower = np.array([0, 0, 60])
    upper = np.array([179, 60, 200])
    
    # Pixels that ARE asphalt
    asphalt_mask = cv2.inRange(hsv, lower, upper)
    
    # Fraction of pixels that are NOT asphalt
    total_pixels = asphalt_mask.size
    non_asphalt = total_pixels - cv2.countNonZero(asphalt_mask)
    non_asphalt_ratio = non_asphalt / total_pixels
    
    return non_asphalt_ratio > empty_threshold


# Define spots (from camera calibration)
spots = [
    {"id": 1, "roi": (300, 400, 100, 250)},
    {"id": 2, "roi": (300, 400, 260, 410)},
    {"id": 3, "roi": (300, 400, 420, 570)},
    # ...
]

# Analyze frame
frame = cv2.imread("parking_lot.jpg")
annotated = frame.copy()

for spot in spots:
    occupied = is_spot_occupied(frame, spot["roi"])
    y1, y2, x1, x2 = spot["roi"]
    
    color = (0, 0, 255) if occupied else (0, 255, 0)  # red = occupied, green = empty
    label = "FULL" if occupied else "EMPTY"
    
    cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
    cv2.putText(annotated, f"#{spot['id']} {label}", (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

cv2.imshow("Parking Status", annotated)
cv2.waitKey(0)
```

---

## Why This Breaks (And What's Next)

Raj tests it at 5 PM: "It says every spot is occupied. Half of them are empty."

The problem: **shadows**. At 5 PM, long shadows fall across the lot. Shadow pixels are dark and slightly blue — they don't match the "asphalt" range. The detector thinks shadows are cars.

```
Noon:                           5 PM:
┌─────────────────────┐        ┌─────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░ │        │ ░░░░░▓▓▓▓░░░░░░░░░ │
│ ░░░ EMPTY ░░░░░░░░░ │        │ ░░░ SHADOW ░░░░░░░ │  ← detector says "occupied"
│ ░░░░░░░░░░░░░░░░░░░ │        │ ░░░░░▓▓▓▓░░░░░░░░░ │
└─────────────────────┘        └─────────────────────┘
```

Solutions (coming in later chapters):
- **Morphological operations** (Ch 6) — clean up noisy masks
- **Background subtraction** (Ch 12) — compare to a known "empty" reference
- **Edge density** — cars have more edges than shadows
- **Texture analysis** — asphalt has uniform texture, cars don't

---

## Histogram: Understanding Pixel Distribution

```python
import matplotlib.pyplot as plt

gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Calculate histogram
hist = cv2.calcHist([gray], [0], None, [256], [0, 256])

plt.figure(figsize=(10, 4))
plt.plot(hist, color='black')
plt.xlabel("Pixel Value (0=black, 255=white)")
plt.ylabel("Count")
plt.title("Grayscale Histogram")
plt.axvline(x=127, color='red', linestyle='--', label='Threshold=127')
plt.legend()
plt.show()
```

The histogram shows you WHERE to set your threshold. A bimodal histogram (two peaks) means Otsu's will work well. A flat histogram means you need adaptive methods.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.threshold(gray, t, max, type) │ Global threshold → binary image
cv2.THRESH_OTSU                 │ Auto-pick threshold from histogram
cv2.adaptiveThreshold(...)      │ Local threshold (handles uneven light)
cv2.cvtColor(img, cv2.COLOR_BGR2HSV) │ Convert to HSV color space
cv2.inRange(hsv, lower, upper)  │ Color range → binary mask
cv2.calcHist(...)               │ Pixel value distribution
cv2.countNonZero(mask)          │ Count white pixels in a mask
HSV: H=0-179, S=0-255, V=0-255 │ Hue, Saturation, Value ranges
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The threshold-based detector works in ideal conditions but fails with shadows and complex scenes. Before we fix that, we need another fundamental tool: edge detection.

Sana: "Cars have edges. Asphalt doesn't. If a spot has lots of edges, something is parked there."

---

[← Chapter 1: Images](chapter-01-images.md) | [Chapter 3: Edge Detection →](chapter-03-edges.md)
