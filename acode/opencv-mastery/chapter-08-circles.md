# Chapter 8: Circle Detection — "Detect Round Things"

[← Chapter 7: Line Detection](chapter-07-lines.md) | [Chapter 9: Geometric Transforms →](chapter-09-transforms.md)

---

## The Task

Raj: "The city requires us to detect the circular 'No Parking' signs at fire lanes. Also, can you detect wheels? If I can see wheels, I know there's a car — even if the body is occluded."

---

## Hough Circle Transform

Like Hough Lines detects lines, Hough Circles detects circular shapes in an image:

```python
import cv2
import numpy as np

img = cv2.imread("parking_lot.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (9, 9), 2)  # blur more for circles

# Detect circles
circles = cv2.HoughCircles(
    blurred,
    cv2.HOUGH_GRADIENT,     # detection method
    dp=1,                   # inverse ratio of accumulator resolution
    minDist=50,             # minimum distance between circle centers
    param1=100,             # upper Canny threshold (lower = param1/2)
    param2=30,              # accumulator threshold (lower = more circles)
    minRadius=10,           # minimum circle radius
    maxRadius=100           # maximum circle radius (0 = no limit)
)

# Draw detected circles
annotated = img.copy()
if circles is not None:
    circles = np.uint16(np.around(circles))
    for circle in circles[0, :]:
        cx, cy, radius = circle
        # Draw the circle outline
        cv2.circle(annotated, (cx, cy), radius, (0, 255, 0), 2)
        # Draw the center
        cv2.circle(annotated, (cx, cy), 2, (0, 0, 255), 3)

    print(f"Found {len(circles[0])} circles")

cv2.imshow("Circles", annotated)
cv2.waitKey(0)
```

---

## Parameters Explained

```python
circles = cv2.HoughCircles(
    image,          # input (grayscale, blurred)
    method,         # cv2.HOUGH_GRADIENT (only option that works well)
    dp,             # 1 = full resolution, 2 = half resolution accumulator
    minDist,        # min pixels between detected circle centers
    param1,         # Canny high threshold (edge sensitivity)
    param2,         # accumulator votes needed (lower = more detections)
    minRadius,      # smallest circle to find
    maxRadius       # largest circle to find
)
```

**Tuning guide:**
- Too many false circles? → Increase `param2` (require more votes)
- Missing circles? → Decrease `param2`, increase blur
- Detecting noise as circles? → Increase `minRadius`, increase blur
- Overlapping detections? → Increase `minDist`

---

## Detecting Parking Signs

Circular parking signs (P, No Parking, Handicap) have specific characteristics:

```python
def detect_circular_signs(frame, min_radius=20, max_radius=80):
    """
    Detect circular signs in a parking lot frame.
    Returns list of (center_x, center_y, radius) tuples.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Strong blur — signs are solid shapes, not fine detail
    blurred = cv2.GaussianBlur(gray, (9, 9), 2)
    
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1.2,
        minDist=60,
        param1=100,
        param2=40,
        minRadius=min_radius,
        maxRadius=max_radius
    )
    
    if circles is None:
        return []
    
    return [(int(c[0]), int(c[1]), int(c[2])) for c in circles[0]]


def classify_sign(frame, cx, cy, radius):
    """
    Classify a detected circular region by its dominant color.
    """
    # Extract the circular ROI
    mask = np.zeros(frame.shape[:2], dtype=np.uint8)
    cv2.circle(mask, (cx, cy), radius, 255, -1)
    
    # Get mean color in the circle
    mean_color = cv2.mean(frame, mask=mask)[:3]  # BGR
    
    hsv_roi = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mean_hsv = cv2.mean(hsv_roi, mask=mask)[:3]
    
    hue, sat, val = mean_hsv
    
    # Classify by color
    if sat < 50:
        return "unknown (gray)"
    elif 0 <= hue <= 10 or 170 <= hue <= 179:
        return "red_sign (no parking?)"
    elif 100 <= hue <= 130:
        return "blue_sign (parking/handicap?)"
    elif 35 <= hue <= 85:
        return "green_sign"
    else:
        return f"colored_sign (hue={hue:.0f})"


# Use it
signs = detect_circular_signs(frame)
for cx, cy, r in signs:
    classification = classify_sign(frame, cx, cy, r)
    print(f"Sign at ({cx}, {cy}) r={r}: {classification}")
```

---

## Detecting Wheels (Partial Circles)

Wheels are harder — they're often partially occluded and have complex internal structure:

```python
def detect_wheels(frame, ground_level_y):
    """
    Detect wheel-like circles near the ground level.
    Wheels are small circles at the bottom of vehicles.
    """
    # Only look at the lower portion of the frame (where wheels are)
    roi = frame[ground_level_y - 50:ground_level_y + 30, :]
    
    gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (7, 7), 1.5)
    
    # Wheels are small circles
    circles = cv2.HoughCircles(
        blurred,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=40,        # wheels are spaced apart
        param1=80,
        param2=25,         # lower threshold (wheels are hard to detect)
        minRadius=8,       # small
        maxRadius=30       # not too big
    )
    
    if circles is None:
        return []
    
    # Adjust y-coordinates back to full frame
    wheels = []
    for c in circles[0]:
        wheels.append((int(c[0]), int(c[1]) + ground_level_y - 50, int(c[2])))
    
    return wheels
```

---

## Combining Circles with Other Detections

```python
def enhanced_vehicle_detection(frame, spots):
    """
    Use multiple signals: contours + edges + circles (wheels).
    """
    results = []
    
    for spot in spots:
        y1, y2, x1, x2 = spot["roi"]
        roi = frame[y1:y2, x1:x2]
        
        # Signal 1: Edge density
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edge_density = cv2.countNonZero(edges) / edges.size
        
        # Signal 2: Circles (wheels) in lower half of spot
        lower_half = blurred[roi.shape[0]//2:, :]
        circles = cv2.HoughCircles(
            lower_half, cv2.HOUGH_GRADIENT,
            dp=1, minDist=20, param1=80, param2=20,
            minRadius=5, maxRadius=25
        )
        has_wheels = circles is not None and len(circles[0]) >= 1
        
        # Combined decision
        occupied = edge_density > 0.08 or has_wheels
        confidence = edge_density + (0.3 if has_wheels else 0)
        
        results.append({
            "id": spot["id"],
            "occupied": occupied,
            "confidence": min(confidence, 1.0),
            "wheels_detected": has_wheels,
        })
    
    return results
```

---

## Common Issues with Circle Detection

### Too many false positives

```python
# Problem: detecting circles everywhere
# Solution: tighter constraints
circles = cv2.HoughCircles(
    blurred,
    cv2.HOUGH_GRADIENT,
    dp=1,
    minDist=80,       # ← increase (circles can't be too close)
    param1=120,       # ← increase (need stronger edges)
    param2=50,        # ← increase (need more votes)
    minRadius=15,     # ← increase (ignore tiny circles)
    maxRadius=60      # ← decrease (ignore huge circles)
)
```

### Missing real circles

```python
# Problem: not detecting circles that are clearly there
# Solution: more blur, lower thresholds
blurred = cv2.GaussianBlur(gray, (11, 11), 3)  # ← more blur
circles = cv2.HoughCircles(
    blurred,
    cv2.HOUGH_GRADIENT,
    dp=1.5,           # ← lower resolution (more forgiving)
    minDist=30,       # ← decrease
    param1=80,        # ← decrease
    param2=20,        # ← decrease (fewer votes needed)
    minRadius=5,
    maxRadius=100
)
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Concept                         │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.HoughCircles(img, method, dp, minDist, p1, p2, minR, maxR) │ Detect circles
dp=1                            │ Full resolution (higher = coarser)
minDist                         │ Min pixels between circle centers
param1                          │ Canny upper threshold
param2                          │ Accumulator votes (lower = more circles)
minRadius / maxRadius           │ Size constraints
Blur heavily before detection   │ Reduces false positives
circles[0, :] → (x, y, r)      │ Output format
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Camera 7 is tilted 15 degrees. Camera 12 has a wide-angle lens that distorts the parking lines into curves. Before your line and circle detection can work reliably across all cameras, you need to correct for perspective and rotation.

Sana: "Geometric transforms. Warp the image so the parking lot looks like a top-down view. Then all your detectors work uniformly."

---

[← Chapter 7: Line Detection](chapter-07-lines.md) | [Chapter 9: Geometric Transforms →](chapter-09-transforms.md)
