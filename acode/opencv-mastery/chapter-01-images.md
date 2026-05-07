# Chapter 1: Loading, Displaying, and Understanding Images

[← Overview](chapter-00-overview.md) | [Chapter 2: Color Spaces & Thresholding →](chapter-02-color-thresholding.md)

---

## The Task

Raj: "Here's a frame from Camera 3. Tell me what you see — dimensions, color info, anything. Prove you can load and manipulate it before we do anything fancy."

---

## Reading an Image

```python
import cv2
import numpy as np

# Load an image from disk
img = cv2.imread("parking_lot.jpg")

# Check if it loaded
if img is None:
    raise FileNotFoundError("Image not found — check the path")

print(f"Shape: {img.shape}")    # (1080, 1920, 3)
print(f"Dtype: {img.dtype}")    # uint8
print(f"Size: {img.size}")      # 6,220,800 (total number of values)
```

`cv2.imread()` returns a NumPy array. The shape is always `(height, width, channels)`.

**Common gotcha:** OpenCV uses **BGR** (Blue, Green, Red), not RGB. If you display with matplotlib, colors will look wrong unless you convert.

---

## Displaying an Image

### With OpenCV (cv2.imshow)

```python
cv2.imshow("Parking Lot", img)
cv2.waitKey(0)            # Wait for any key press
cv2.destroyAllWindows()   # Close the window
```

- `waitKey(0)` → wait forever until a key is pressed
- `waitKey(30)` → wait 30ms (useful for video loops)

### With Matplotlib (for Jupyter / scripts)

```python
import matplotlib.pyplot as plt

# Convert BGR → RGB for correct colors
img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

plt.figure(figsize=(12, 8))
plt.imshow(img_rgb)
plt.title("Parking Lot - Camera 3")
plt.axis("off")
plt.show()
```

---

## Pixel Access

Every pixel is an array of 3 values (BGR):

```python
# Get the pixel at row 100, column 200
pixel = img[100, 200]
print(pixel)  # [142, 158, 173] → [Blue, Green, Red]

# Access individual channels
blue = img[100, 200, 0]
green = img[100, 200, 1]
red = img[100, 200, 2]

# Set a pixel to pure red (BGR = 0, 0, 255)
img[100, 200] = [0, 0, 255]
```

**Don't loop over pixels in Python.** It's catastrophically slow. Use NumPy operations instead:

```python
# BAD — 2 million iterations, takes 10+ seconds
for y in range(img.shape[0]):
    for x in range(img.shape[1]):
        img[y, x] = [255, 255, 255]

# GOOD — vectorized, instant
img[:] = [255, 255, 255]
```

---

## Regions of Interest (ROI)

A ROI is just array slicing:

```python
# Crop a region: rows 100-300, columns 200-500
roi = img[100:300, 200:500]

print(roi.shape)  # (200, 300, 3)

# Show just the ROI
cv2.imshow("ROI", roi)
cv2.waitKey(0)
```

This is how you'll isolate parking spots, license plates, or specific zones:

```python
# Define parking spot regions (from camera calibration)
spots = [
    {"id": 1, "roi": (50, 100, 200, 300)},   # (y1, y2, x1, x2)
    {"id": 2, "roi": (50, 100, 310, 510)},
    {"id": 3, "roi": (50, 100, 520, 720)},
]

for spot in spots:
    y1, y2, x1, x2 = spot["roi"]
    spot_img = img[y1:y2, x1:x2]
    # Analyze this spot...
```

---

## Image Properties

```python
height, width, channels = img.shape
total_pixels = height * width
total_values = img.size  # height * width * channels
memory_bytes = img.nbytes  # actual memory usage

print(f"Resolution: {width}x{height}")
print(f"Channels: {channels}")
print(f"Total pixels: {total_pixels:,}")
print(f"Memory: {memory_bytes / 1024 / 1024:.1f} MB")
```

A 1920×1080 color image = ~6 MB in memory. At 30 fps, that's 180 MB/s of data per camera. This is why performance matters (Chapter 16).

---

## Resizing

```python
# Resize to specific dimensions
small = cv2.resize(img, (640, 480))  # (width, height) — note the order!

# Resize by scale factor
half = cv2.resize(img, None, fx=0.5, fy=0.5)

# Resize with different interpolation
# INTER_AREA — best for shrinking
# INTER_LINEAR — default, good for enlarging
# INTER_CUBIC — slower but smoother enlarging
thumbnail = cv2.resize(img, (320, 240), interpolation=cv2.INTER_AREA)
```

**Note:** `cv2.resize()` takes `(width, height)` but `img.shape` returns `(height, width, channels)`. This inconsistency trips up everyone.

---

## Color Conversion

```python
# BGR to Grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
print(gray.shape)  # (1080, 1920) — single channel, no 3rd dimension

# BGR to HSV (Hue, Saturation, Value)
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

# BGR to RGB (for matplotlib)
rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
```

Grayscale reduces 3 channels to 1. Every pixel is a single value 0-255 (black to white). Most detection algorithms work on grayscale — color is often irrelevant.

---

## Drawing on Images

```python
# Make a copy (don't draw on the original)
annotated = img.copy()

# Rectangle (top-left corner, bottom-right corner)
cv2.rectangle(annotated, (200, 100), (500, 300), (0, 255, 0), 2)
#                         pt1          pt2         color(BGR)  thickness

# Circle (center, radius)
cv2.circle(annotated, (350, 200), 50, (0, 0, 255), -1)  # -1 = filled

# Line
cv2.line(annotated, (0, 540), (1920, 540), (255, 0, 0), 1)

# Text
cv2.putText(annotated, "Spot 1: OCCUPIED", (210, 90),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

cv2.putText(annotated, "Spot 2: EMPTY", (520, 90),
            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
```

Drawing is how you'll visualize detections — bounding boxes around cars, labels on spots, lines showing zones.

---

## Saving Images

```python
# Save to disk
cv2.imwrite("output/annotated_lot.jpg", annotated)

# Save with quality settings
cv2.imwrite("output/high_quality.jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 95])
cv2.imwrite("output/compressed.jpg", annotated, [cv2.IMWRITE_JPEG_QUALITY, 50])

# Save as PNG (lossless)
cv2.imwrite("output/lossless.png", annotated)
```

---

## Channels: Split and Merge

```python
# Split into individual channels
b, g, r = cv2.split(img)

# Each channel is a grayscale image
print(b.shape)  # (1080, 1920)

# Merge channels back
merged = cv2.merge([b, g, r])

# Visualize individual channels
cv2.imshow("Blue Channel", b)
cv2.imshow("Green Channel", g)
cv2.imshow("Red Channel", r)
cv2.waitKey(0)
```

---

## Arithmetic Operations

```python
# Brighten an image (add to all pixels)
bright = cv2.add(img, np.full_like(img, 50))  # clips at 255

# Darken
dark = cv2.subtract(img, np.full_like(img, 50))  # clips at 0

# Blend two images (weighted addition)
blended = cv2.addWeighted(img1, 0.7, img2, 0.3, 0)
# result = img1 * 0.7 + img2 * 0.3 + 0

# Why cv2.add() instead of img + 50?
# NumPy wraps: 250 + 10 = 4 (overflow!)
# cv2.add clips: 250 + 10 = 255 (correct)
```

---

## Putting It Together: First Analysis

```python
import cv2
import numpy as np

def analyze_frame(frame_path):
    """Basic frame analysis for ParkEye."""
    img = cv2.imread(frame_path)
    if img is None:
        raise FileNotFoundError(f"Cannot load: {frame_path}")

    h, w, c = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Basic statistics
    mean_brightness = np.mean(gray)
    std_brightness = np.std(gray)

    print(f"Resolution: {w}x{h}")
    print(f"Mean brightness: {mean_brightness:.1f} / 255")
    print(f"Brightness std: {std_brightness:.1f}")

    if mean_brightness < 50:
        print("⚠️  Very dark — night mode needed")
    elif mean_brightness > 200:
        print("⚠️  Very bright — possible glare")
    else:
        print("✅ Lighting looks reasonable")

    # Show with annotation
    annotated = img.copy()
    cv2.putText(annotated, f"Brightness: {mean_brightness:.0f}/255",
                (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Analysis", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    return {
        "width": w,
        "height": h,
        "mean_brightness": mean_brightness,
        "std_brightness": std_brightness,
    }


if __name__ == "__main__":
    stats = analyze_frame("parking_lot.jpg")
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.imread(path)                │ Load image → NumPy array (BGR)
cv2.imshow(name, img)           │ Display in a window
cv2.waitKey(ms)                 │ Wait for key (0 = forever)
cv2.destroyAllWindows()         │ Close all windows
cv2.imwrite(path, img)          │ Save image to disk
cv2.resize(img, (w, h))        │ Resize (note: width, height order)
cv2.cvtColor(img, code)         │ Convert color space
cv2.rectangle(img, pt1, pt2, color, thickness) │ Draw rectangle
cv2.circle(img, center, r, color, thickness)   │ Draw circle
cv2.putText(img, text, pos, font, scale, color, thickness) │ Draw text
img[y1:y2, x1:x2]              │ Crop ROI (region of interest)
img.shape                       │ (height, width, channels)
img.copy()                      │ Deep copy (safe to modify)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Raj: "OK, you can load images. Now tell me: is parking spot #7 empty or occupied? The camera sees it. You need to decide."

That requires understanding color — specifically, how to separate "asphalt gray" from "car-colored" pixels. That's color spaces and thresholding.

---

[← Overview](chapter-00-overview.md) | [Chapter 2: Color Spaces & Thresholding →](chapter-02-color-thresholding.md)
