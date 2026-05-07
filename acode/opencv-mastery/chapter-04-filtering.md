# Chapter 4: Filtering — "The Image Is Noisy"

[← Chapter 3: Edge Detection](chapter-03-edges.md) | [Chapter 5: Contours →](chapter-05-contours.md)

---

## The Problem

You run Canny on Camera 7's feed. The result is a mess — hundreds of tiny edge fragments that aren't real edges. They're noise from the dirty lens, compression artifacts, and sensor grain.

Sana: "Never run edge detection on a raw image. Always filter first. A good blur kills noise but keeps the real edges intact. The trick is choosing the right blur."

---

## Why Filter?

```
Raw image → Canny:          Filtered image → Canny:
┌─────────────────────┐     ┌─────────────────────┐
│ ·.·:.·:·.·:·.·:·.· │     │                     │
│ ·:CAR OUTLINE:·.·:· │     │   ┌───────────┐     │
│ ·.·:.·:·.·:·.·:·.· │     │   │           │     │
│ ·:·.·:·.·:·.·:·.·: │     │   └───────────┘     │
│ ·.·:.·:·.·:·.·:·.· │     │                     │
└─────────────────────┘     └─────────────────────┘
  Noise everywhere             Clean edges only
```

Filtering = smoothing = blurring. It averages nearby pixels, which eliminates small random variations (noise) while preserving large changes (real edges).

---

## Gaussian Blur: The Default Choice

Gaussian blur weights nearby pixels by distance — closer pixels contribute more. It's the most natural-looking blur and the best general-purpose filter.

```python
import cv2
import numpy as np

img = cv2.imread("parking_lot.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Gaussian blur with 5x5 kernel
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
#                                ksize    sigmaX (0 = auto from ksize)

# Compare edge detection with and without blur
edges_raw = cv2.Canny(gray, 50, 150)
edges_blurred = cv2.Canny(blurred, 50, 150)

cv2.imshow("Edges (no blur)", edges_raw)
cv2.imshow("Edges (Gaussian blur)", edges_blurred)
cv2.waitKey(0)
```

### Kernel Size

- `(3, 3)` → light blur, preserves fine detail
- `(5, 5)` → moderate blur (good default)
- `(7, 7)` → stronger blur
- `(15, 15)` → heavy blur, only large structures survive

Must be odd numbers. Larger kernel = more smoothing = fewer false edges but also fewer real edges.

```python
# Visualize different kernel sizes
for k in [3, 5, 7, 11, 15]:
    blurred = cv2.GaussianBlur(gray, (k, k), 0)
    edges = cv2.Canny(blurred, 50, 150)
    edge_count = cv2.countNonZero(edges)
    print(f"Kernel {k}x{k}: {edge_count} edge pixels")
    cv2.imshow(f"k={k}", edges)

cv2.waitKey(0)
```

---

## Median Blur: Salt-and-Pepper Noise Killer

Median blur replaces each pixel with the **median** of its neighbors. It's exceptional at removing salt-and-pepper noise (random black/white pixels) while preserving edges better than Gaussian.

```python
# Median blur — great for impulse noise
median = cv2.medianBlur(gray, 5)  # kernel size must be odd

# Compare on noisy image
noisy = gray.copy()
# Add salt-and-pepper noise
num_noise = 5000
coords = [np.random.randint(0, i - 1, num_noise) for i in gray.shape]
noisy[coords[0], coords[1]] = 255  # salt
coords = [np.random.randint(0, i - 1, num_noise) for i in gray.shape]
noisy[coords[0], coords[1]] = 0    # pepper

gaussian_fix = cv2.GaussianBlur(noisy, (5, 5), 0)
median_fix = cv2.medianBlur(noisy, 5)

cv2.imshow("Noisy", noisy)
cv2.imshow("Gaussian (blurs everything)", gaussian_fix)
cv2.imshow("Median (removes noise, keeps edges)", median_fix)
cv2.waitKey(0)
```

Median wins for salt-and-pepper because outlier pixels (0 or 255) never survive the median calculation.

---

## Bilateral Filter: Blur Without Losing Edges

The problem with Gaussian: it blurs EVERYTHING, including edges. Bilateral filter blurs flat regions but preserves edges by considering both spatial distance AND intensity difference.

```python
# Bilateral filter — smooths flat areas, keeps edges sharp
bilateral = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)
#                                      diameter  color_sigma  space_sigma

cv2.imshow("Original", gray)
cv2.imshow("Gaussian (edges blurred)", cv2.GaussianBlur(gray, (9, 9), 0))
cv2.imshow("Bilateral (edges preserved)", bilateral)
cv2.waitKey(0)
```

Parameters:
- `d` → diameter of pixel neighborhood (use -1 to compute from sigmaSpace)
- `sigmaColor` → larger = more colors mixed together (more smoothing)
- `sigmaSpace` → larger = farther pixels influence each other

**Tradeoff:** Bilateral is 5-10× slower than Gaussian. Use it when edge preservation matters more than speed.

---

## Box Filter (Average Blur)

The simplest blur — every pixel becomes the average of its neighbors. Fast but produces blocky artifacts.

```python
# Box filter — simple average
box = cv2.blur(gray, (5, 5))

# Equivalent to:
kernel = np.ones((5, 5), np.float32) / 25
box_manual = cv2.filter2D(gray, -1, kernel)
```

Rarely the best choice, but useful to understand how convolution works.

---

## How Convolution Works

All these filters work by **convolution** — sliding a small matrix (kernel) over the image and computing a weighted sum at each position:

```
Image region:          Gaussian kernel (3x3):       Result:
┌─────────────┐       ┌─────────────┐
│ 100 120 110 │       │ 1/16  2/16  1/16 │       weighted sum
│ 105 200 115 │   ×   │ 2/16  4/16  2/16 │   =   of all 9 products
│ 108 118 112 │       │ 1/16  2/16  1/16 │
└─────────────┘       └─────────────┘

The center pixel (200) becomes a weighted average of itself and its neighbors.
High weight on center (4/16), low weight on corners (1/16).
```

```python
# Custom kernel — you can make your own filters
# Sharpen kernel
sharpen_kernel = np.array([
    [ 0, -1,  0],
    [-1,  5, -1],
    [ 0, -1,  0]
], dtype=np.float32)

sharpened = cv2.filter2D(gray, -1, sharpen_kernel)

# Emboss kernel
emboss_kernel = np.array([
    [-2, -1, 0],
    [-1,  1, 1],
    [ 0,  1, 2]
], dtype=np.float32)

embossed = cv2.filter2D(gray, -1, emboss_kernel)
```

---

## Practical: Preprocessing Pipeline for ParkEye

```python
def preprocess_frame(frame, camera_id):
    """
    Standard preprocessing for ParkEye camera frames.
    Handles noise, lighting normalization, and prepares for detection.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Camera 7 has a dirty lens — needs stronger filtering
    if camera_id == 7:
        # Median first (removes speckle from dirty lens)
        gray = cv2.medianBlur(gray, 5)
        # Then light Gaussian (smooth remaining noise)
        gray = cv2.GaussianBlur(gray, (3, 3), 0)
    else:
        # Standard cameras — light Gaussian is enough
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    return gray


def detect_with_preprocessing(frame, roi, camera_id):
    """Full detection pipeline with proper preprocessing."""
    preprocessed = preprocess_frame(frame, camera_id)
    
    y1, y2, x1, x2 = roi
    spot = preprocessed[y1:y2, x1:x2]
    
    # Now edge detection works cleanly
    edges = cv2.Canny(spot, 50, 150)
    density = cv2.countNonZero(edges) / edges.size
    
    return density > 0.10
```

---

## Noise Types and Best Filters

```
Noise Type              │ Looks Like              │ Best Filter
────────────────────────┼─────────────────────────┼──────────────────
Gaussian noise          │ Grainy, like film grain │ Gaussian blur
Salt-and-pepper         │ Random black/white dots │ Median blur
Speckle (multiplicative)│ Granular texture        │ Bilateral or median
Compression artifacts   │ Blocky edges (JPEG)     │ Bilateral
Sensor noise (low light)│ Color speckles          │ fastNlMeansDenoising
```

---

## Advanced: Non-Local Means Denoising

For serious noise (night cameras, high ISO), OpenCV has a dedicated denoiser:

```python
# Non-local means denoising — slow but excellent quality
# For grayscale
denoised = cv2.fastNlMeansDenoising(gray, h=10, templateWindowSize=7, searchWindowSize=21)

# For color images
denoised_color = cv2.fastNlMeansDenoisingColored(img, h=10, hForColorComponents=10,
                                                   templateWindowSize=7, searchWindowSize=21)
```

- `h` → filter strength (higher = more denoising, more detail loss)
- Much slower than Gaussian/median (not real-time for HD)
- Best for offline processing or small ROIs

---

## The Blur → Edge Pipeline

The standard pattern you'll use throughout this course:

```python
def clean_edges(gray, blur_ksize=5, canny_low=50, canny_high=150):
    """The fundamental preprocessing → detection pipeline."""
    # Step 1: Remove noise
    blurred = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)
    
    # Step 2: Detect edges on clean image
    edges = cv2.Canny(blurred, canny_low, canny_high)
    
    return edges
```

This two-step pattern (filter → detect) is the foundation of everything that follows.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.GaussianBlur(img, (k,k), 0)│ Smooth blur, good default
cv2.medianBlur(img, k)          │ Kills salt-and-pepper noise
cv2.bilateralFilter(img, d, σc, σs) │ Smooths flat areas, keeps edges
cv2.blur(img, (k,k))           │ Simple average (box filter)
cv2.filter2D(img, -1, kernel)  │ Apply custom kernel
cv2.fastNlMeansDenoising(...)  │ Heavy denoising (slow)
Kernel size: odd numbers only   │ 3, 5, 7, 9, 11...
Larger kernel = more smoothing  │ But also more detail loss
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You can now load images, threshold them, detect edges, and filter noise. The next step: finding **shapes**. When you threshold or edge-detect, you get a binary image. Contours extract the boundaries of white regions as lists of points — giving you shape, area, position, and bounding boxes.

Raj: "Don't just tell me there are edges. Tell me WHERE the car is. Give me a bounding box."

---

[← Chapter 3: Edge Detection](chapter-03-edges.md) | [Chapter 5: Contours →](chapter-05-contours.md)
