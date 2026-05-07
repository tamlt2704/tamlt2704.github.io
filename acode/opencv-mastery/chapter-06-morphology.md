# Chapter 6: Morphological Operations — "Shadows Break Everything"

[← Chapter 5: Contours](chapter-05-contours.md) | [Chapter 7: Line Detection →](chapter-07-lines.md)

---

## The Problem

It's 5 PM. Long shadows stretch across the parking lot. Your threshold creates a binary mask where shadows connect separate cars into one giant blob. Small noise dots create hundreds of false contours. The detector is useless.

Sana: "Morphology. It's the cleanup crew for binary images. Erosion shrinks white regions (kills noise). Dilation expands them (fills gaps). Combine them and you get clean masks."

---

## The Core Operations

### Erosion: Shrink White Regions

Erosion slides a kernel over the image. A white pixel stays white ONLY if ALL pixels under the kernel are white. Otherwise it becomes black.

Effect: white regions shrink. Small white dots disappear. Thin connections break.

```python
import cv2
import numpy as np

img = cv2.imread("parking_lot.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
_, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

# Create a kernel (structuring element)
kernel = np.ones((5, 5), np.uint8)

# Erode — shrink white regions
eroded = cv2.erode(binary, kernel, iterations=1)

cv2.imshow("Original", binary)
cv2.imshow("Eroded", eroded)
cv2.waitKey(0)
```

### Dilation: Expand White Regions

Dilation is the opposite. A pixel becomes white if ANY pixel under the kernel is white.

Effect: white regions grow. Small gaps fill. Nearby blobs merge.

```python
# Dilate — expand white regions
dilated = cv2.dilate(binary, kernel, iterations=1)

cv2.imshow("Dilated", dilated)
cv2.waitKey(0)
```

---

## Iterations: How Much to Apply

```python
# More iterations = stronger effect
eroded_1 = cv2.erode(binary, kernel, iterations=1)  # light
eroded_2 = cv2.erode(binary, kernel, iterations=2)  # moderate
eroded_3 = cv2.erode(binary, kernel, iterations=3)  # aggressive

# Same for dilation
dilated_1 = cv2.dilate(binary, kernel, iterations=1)
dilated_3 = cv2.dilate(binary, kernel, iterations=3)
```

---

## Opening: Erosion → Dilation (Remove Noise)

Opening = erode first (kill small white dots), then dilate (restore the size of remaining objects).

Net effect: small noise disappears, large objects stay roughly the same size.

```python
# Opening — removes small white noise
kernel = np.ones((5, 5), np.uint8)
opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

# Equivalent to:
# opened = cv2.dilate(cv2.erode(binary, kernel), kernel)
```

**Use case:** Your threshold creates tiny white speckles that aren't cars. Opening removes them.

---

## Closing: Dilation → Erosion (Fill Gaps)

Closing = dilate first (fill small black holes), then erode (restore size).

Net effect: small gaps inside objects fill in, objects stay roughly the same size.

```python
# Closing — fills small holes in white regions
closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

# Equivalent to:
# closed = cv2.erode(cv2.dilate(binary, kernel), kernel)
```

**Use case:** A car's binary mask has gaps (windows are dark, creating holes). Closing fills them so the car is one solid blob.

---

## Visual Summary

```
Operation    │ What It Does                    │ When to Use
─────────────┼─────────────────────────────────┼──────────────────────────
Erosion      │ Shrinks white, removes thin     │ Separate touching objects
Dilation     │ Expands white, fills small gaps  │ Connect nearby fragments
Opening      │ Erode → Dilate                  │ Remove small noise dots
Closing      │ Dilate → Erode                  │ Fill holes inside objects
```

```
Original:        Erosion:         Dilation:        Opening:         Closing:
██·█████·██     ··· ███ ···     ████████████     ··· █████ ···    ███████████
█·██·████·█     ··· █·██ ··     ████·████·█      ··· █████ ···    ███████████
·███████··█     ·· █████ ··     ████████████     ··· █████ ···    ███████████
                                                 (noise gone)     (holes filled)
```

---

## Structuring Elements (Kernels)

The kernel shape matters:

```python
# Rectangle (default) — good for general use
rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))

# Ellipse — smoother, more natural
ellipse_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))

# Cross — only affects horizontal/vertical neighbors
cross_kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (5, 5))

# Visualize them
print("Rectangle:\n", rect_kernel)
print("Ellipse:\n", ellipse_kernel)
print("Cross:\n", cross_kernel)
```

```
Rectangle:     Ellipse:       Cross:
1 1 1 1 1     0 0 1 0 0     0 0 1 0 0
1 1 1 1 1     1 1 1 1 1     0 0 1 0 0
1 1 1 1 1     1 1 1 1 1     1 1 1 1 1
1 1 1 1 1     1 1 1 1 1     0 0 1 0 0
1 1 1 1 1     0 0 1 0 0     0 0 1 0 0
```

Ellipse is often best for natural objects (cars, people). Rectangle can create blocky artifacts.

---

## Gradient: Edge Detection via Morphology

Morphological gradient = dilation - erosion. It gives you the outline of objects:

```python
# Morphological gradient — outlines of white regions
gradient = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel)
```

---

## Top Hat and Black Hat

```python
# Top Hat = original - opening
# Reveals bright spots smaller than the kernel (small bright objects on dark background)
tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)

# Black Hat = closing - original
# Reveals dark spots smaller than the kernel (small dark objects on bright background)
blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
```

**Use case for ParkEye:** Top hat can highlight license plate characters (small bright regions on a dark plate).

---

## Practical: The Shadow Problem Solved

```python
def clean_parking_mask(frame, spot_roi):
    """
    Create a clean binary mask for a parking spot,
    robust to shadows and noise.
    """
    y1, y2, x1, x2 = spot_roi
    spot = frame[y1:y2, x1:x2]
    
    # Convert to HSV — shadows have low saturation
    hsv = cv2.cvtColor(spot, cv2.COLOR_BGR2HSV)
    
    # Threshold on saturation (shadows are gray = low saturation)
    # Cars are colorful = higher saturation
    saturation = hsv[:, :, 1]
    _, sat_mask = cv2.threshold(saturation, 40, 255, cv2.THRESH_BINARY)
    
    # Also use edge information
    gray = cv2.cvtColor(spot, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    
    # Dilate edges to connect nearby edge fragments
    edge_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    edges_dilated = cv2.dilate(edges, edge_kernel, iterations=2)
    
    # Combine: pixel is "car" if it has saturation OR edges
    combined = cv2.bitwise_or(sat_mask, edges_dilated)
    
    # Opening: remove small noise
    open_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    cleaned = cv2.morphologyEx(combined, cv2.MORPH_OPEN, open_kernel)
    
    # Closing: fill gaps inside the car
    close_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, close_kernel)
    
    return cleaned


def is_spot_occupied_v5(frame, spot_roi, threshold=0.25):
    """
    v5: Shadow-robust parking detection using morphology.
    """
    mask = clean_parking_mask(frame, spot_roi)
    fill_ratio = cv2.countNonZero(mask) / mask.size
    return fill_ratio > threshold
```

---

## Before and After: The Full Pipeline

```python
def full_detection_pipeline(frame, spots):
    """
    Complete parking detection with preprocessing and morphology.
    This is what production looks like.
    """
    annotated = frame.copy()
    results = []
    
    for spot in spots:
        y1, y2, x1, x2 = spot["roi"]
        
        # Get clean mask
        mask = clean_parking_mask(frame, spot["roi"])
        
        # Find contours in clean mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate metrics
        fill_ratio = cv2.countNonZero(mask) / mask.size
        num_contours = len([c for c in contours if cv2.contourArea(c) > 100])
        
        occupied = fill_ratio > 0.25
        
        # Annotate
        color = (0, 0, 255) if occupied else (0, 255, 0)
        cv2.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        label = f"#{spot['id']} {'FULL' if occupied else 'EMPTY'} ({fill_ratio:.0%})"
        cv2.putText(annotated, label, (x1, y1 - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
        
        results.append({"id": spot["id"], "occupied": occupied, "fill": fill_ratio})
    
    return annotated, results
```

---

## Common Morphology Recipes

```python
# Recipe 1: Remove noise, then find clean contours
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
clean = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
contours, _ = cv2.findContours(clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Recipe 2: Connect broken edges into closed shapes
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
connected = cv2.dilate(edges, kernel, iterations=2)
connected = cv2.morphologyEx(connected, cv2.MORPH_CLOSE, kernel)

# Recipe 3: Separate touching objects
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
separated = cv2.erode(binary, kernel, iterations=2)

# Recipe 4: Extract object boundaries
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
boundary = cv2.morphologyEx(binary, cv2.MORPH_GRADIENT, kernel)
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.erode(img, kernel, iter)    │ Shrink white regions
cv2.dilate(img, kernel, iter)   │ Expand white regions
cv2.morphologyEx(img, op, kernel) │ Combined operations
cv2.MORPH_OPEN                  │ Erode → Dilate (remove noise)
cv2.MORPH_CLOSE                 │ Dilate → Erode (fill holes)
cv2.MORPH_GRADIENT              │ Dilation - Erosion (outlines)
cv2.MORPH_TOPHAT                │ Original - Opening (bright details)
cv2.MORPH_BLACKHAT              │ Closing - Original (dark details)
cv2.getStructuringElement(shape, size) │ Create kernel
cv2.MORPH_RECT / ELLIPSE / CROSS │ Kernel shapes
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You can now detect objects robustly — even with shadows and noise. But Raj has a new request: "Find the painted parking lines. I need to know where spots BEGIN and END, not just whether something is in them."

That's line detection — Hough transforms.

---

[← Chapter 5: Contours](chapter-05-contours.md) | [Chapter 7: Line Detection →](chapter-07-lines.md)
