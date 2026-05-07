# Chapter 3: Edge Detection — "Find the Edges of Cars"

[← Chapter 2: Color & Thresholding](chapter-02-color-thresholding.md) | [Chapter 4: Filtering →](chapter-04-filtering.md)

---

## The Task

Sana: "Thresholding alone won't cut it. Shadows have similar brightness to dark cars. But shadows don't have edges — cars do. Edges are where pixel intensity changes sharply. Use that."

---

## What Is an Edge?

An edge is a boundary where pixel values change rapidly. In a parking lot:
- The outline of a car → strong edges
- Painted lines on the ground → edges
- Shadow boundaries → weak edges
- Flat asphalt → no edges

```
Pixel values across a car boundary:

  150 150 150 148 145 │ 40  35  30  32  35
  ─────────────────────┼──────────────────────
  asphalt (bright)     │  car roof (dark)
                       │
                    EDGE (sharp change)
```

---

## Sobel Operator: Directional Gradients

Sobel detects edges in one direction (horizontal or vertical) by computing the derivative of pixel intensity:

```python
import cv2
import numpy as np

img = cv2.imread("parking_lot.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Horizontal edges (changes in Y direction)
sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)

# Vertical edges (changes in X direction)
sobel_y = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

# Combine both directions (magnitude)
magnitude = np.sqrt(sobel_x**2 + sobel_y**2)
magnitude = np.uint8(np.clip(magnitude, 0, 255))

cv2.imshow("Sobel X (horizontal edges)", np.uint8(np.abs(sobel_x)))
cv2.imshow("Sobel Y (vertical edges)", np.uint8(np.abs(sobel_y)))
cv2.imshow("Combined", magnitude)
cv2.waitKey(0)
```

- `cv2.CV_64F` → output as float (edges can be negative)
- `ksize=3` → 3×3 kernel (larger = smoother but less precise)
- `1, 0` → derivative in X direction (detects vertical edges)
- `0, 1` → derivative in Y direction (detects horizontal edges)

---

## Canny Edge Detection: The Standard

Canny is the go-to edge detector. It's multi-step:
1. Gaussian blur (reduce noise)
2. Gradient calculation (Sobel in both directions)
3. Non-maximum suppression (thin edges to 1 pixel wide)
4. Hysteresis thresholding (connect strong edges, discard weak ones)

```python
# Canny edge detection
edges = cv2.Canny(gray, 50, 150)
#                       low_thresh  high_thresh

cv2.imshow("Canny Edges", edges)
cv2.waitKey(0)
```

### The Two Thresholds

- **High threshold (150):** Gradient above this → definitely an edge
- **Low threshold (50):** Gradient below this → definitely NOT an edge
- **Between:** Only an edge if connected to a strong edge

```
Gradient value:    0 ──────── 50 ──────── 150 ──────── 255
                   │  NOT edge  │  maybe    │  EDGE      │
                   │            │ (only if  │            │
                   │            │ connected │            │
                   │            │ to edge)  │            │
```

Rule of thumb: `high_threshold = 2× or 3× low_threshold`

---

## Choosing Canny Thresholds

```python
def auto_canny(gray, sigma=0.33):
    """Automatically determine Canny thresholds from the median."""
    median = np.median(gray)
    lower = int(max(0, (1.0 - sigma) * median))
    upper = int(min(255, (1.0 + sigma) * median))
    return cv2.Canny(gray, lower, upper)

edges = auto_canny(gray)
```

Or use a trackbar to find good values interactively:

```python
def nothing(x):
    pass

cv2.namedWindow("Canny")
cv2.createTrackbar("Low", "Canny", 50, 255, nothing)
cv2.createTrackbar("High", "Canny", 150, 255, nothing)

while True:
    low = cv2.getTrackbarPos("Low", "Canny")
    high = cv2.getTrackbarPos("High", "Canny")
    edges = cv2.Canny(gray, low, high)
    cv2.imshow("Canny", edges)
    if cv2.waitKey(30) == 27:  # ESC to exit
        break
```

---

## Edge Density: A Better Parking Detector

Sana's insight: cars have lots of edges (body panels, windows, wheels, shadows). Empty asphalt has almost none.

```python
def edge_density(frame, roi):
    """
    Calculate edge density in a region.
    High density = something is there (car).
    Low density = empty (asphalt).
    """
    y1, y2, x1, x2 = roi
    spot = frame[y1:y2, x1:x2]
    
    gray = cv2.cvtColor(spot, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    
    # Fraction of pixels that are edges
    total_pixels = edges.size
    edge_pixels = cv2.countNonZero(edges)
    density = edge_pixels / total_pixels
    
    return density


def is_spot_occupied_v2(frame, roi, threshold=0.10):
    """
    v2: Uses edge density instead of color thresholding.
    More robust to shadows and lighting changes.
    """
    density = edge_density(frame, roi)
    return density > threshold


# Test it
frame = cv2.imread("parking_lot.jpg")
spots = [
    {"id": 1, "roi": (300, 400, 100, 250)},
    {"id": 2, "roi": (300, 400, 260, 410)},
]

for spot in spots:
    density = edge_density(frame, spot["roi"])
    occupied = density > 0.10
    print(f"Spot {spot['id']}: density={density:.3f} → {'OCCUPIED' if occupied else 'EMPTY'}")
```

---

## Why Edge Density Beats Thresholding

```
                    Color Threshold    Edge Density
                    ──────────────     ────────────
Shadow on asphalt:  "OCCUPIED" ❌      "EMPTY" ✅ (shadows have few edges)
Dark car:           "EMPTY" ❌         "OCCUPIED" ✅ (car has many edges)
White car:          "EMPTY" ❌         "OCCUPIED" ✅ (still has edges)
Wet asphalt:        "OCCUPIED" ❌      "EMPTY" ✅ (wet surface = few edges)
```

Edge density is more robust because it measures **structure**, not color. Cars have structure. Empty pavement doesn't.

---

## Combining Both Approaches

The best detector uses multiple signals:

```python
def is_spot_occupied_v3(frame, roi):
    """
    v3: Combines color analysis + edge density.
    More robust than either alone.
    """
    y1, y2, x1, x2 = roi
    spot = frame[y1:y2, x1:x2]
    
    # Signal 1: Edge density
    gray = cv2.cvtColor(spot, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_ratio = cv2.countNonZero(edges) / edges.size
    
    # Signal 2: Color variance (cars are more colorful than asphalt)
    hsv = cv2.cvtColor(spot, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    sat_mean = np.mean(saturation)
    
    # Signal 3: Brightness difference from expected asphalt
    value = hsv[:, :, 2]
    val_std = np.std(value)
    
    # Weighted decision
    score = (
        (edge_ratio > 0.08) * 0.5 +    # edges present
        (sat_mean > 40) * 0.3 +          # colorful
        (val_std > 30) * 0.2             # brightness variation
    )
    
    return score > 0.4
```

---

## Laplacian: Second Derivative

The Laplacian detects edges in all directions at once (second derivative):

```python
# Laplacian — detects all edges (no direction preference)
laplacian = cv2.Laplacian(gray, cv2.CV_64F)
laplacian = np.uint8(np.abs(laplacian))

cv2.imshow("Laplacian", laplacian)
```

Laplacian is noisier than Canny but useful for detecting "how much texture" a region has:

```python
# Variance of Laplacian = measure of image sharpness/texture
def texture_score(gray_roi):
    lap = cv2.Laplacian(gray_roi, cv2.CV_64F)
    return lap.var()

# High variance = lots of texture (car, tree, person)
# Low variance = flat surface (asphalt, wall, sky)
```

---

## Edge Detection Comparison

```
Method      │ Speed  │ Quality │ When to Use
────────────┼────────┼─────────┼──────────────────────────────
Sobel       │ Fast   │ OK      │ Need directional edges only
Canny       │ Medium │ Best    │ General edge detection (default choice)
Laplacian   │ Fast   │ Noisy   │ Texture/sharpness measurement
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.Canny(gray, low, high)      │ Best general edge detector
cv2.Sobel(gray, ddepth, dx, dy) │ Directional gradient (edges in x or y)
cv2.Laplacian(gray, ddepth)     │ Second derivative (all-direction edges)
Edge density = edges/total      │ Fraction of pixels that are edges
auto_canny(gray, sigma=0.33)    │ Auto-threshold Canny from median
Canny rule: high ≈ 2-3× low    │ Threshold ratio guideline
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The edge detector works, but it's picking up noise — tiny speckles that aren't real edges. Camera 7 (the dirty one) is especially bad. Before we can reliably detect shapes, we need to clean up the image.

Sana: "Always blur before edge detection. Noise creates fake edges. A Gaussian blur kills the noise but preserves the real structure."

---

[← Chapter 2: Color & Thresholding](chapter-02-color-thresholding.md) | [Chapter 4: Filtering →](chapter-04-filtering.md)
