# Chapter 5: Contours — "Find the Shape of Things"

[← Chapter 4: Filtering](chapter-04-filtering.md) | [Chapter 6: Morphology →](chapter-06-morphology.md)

---

## The Task

Raj: "I don't want pixel counts. I want bounding boxes. 'There's a car at position (x, y) with size (w, h).' Give me objects, not pixels."

---

## What Are Contours?

A contour is the boundary of a connected white region in a binary image. It's a list of (x, y) points that trace the outline of a shape.

```
Binary image:              Contours found:
┌─────────────────────┐   ┌─────────────────────┐
│                     │   │                     │
│   ████████          │   │   ┌──────┐          │
│   ████████          │   │   │      │          │
│   ████████          │   │   └──────┘          │
│                     │   │                     │
│        ██████████   │   │        ┌────────┐   │
│        ██████████   │   │        │        │   │
│        ██████████   │   │        └────────┘   │
│                     │   │                     │
└─────────────────────┘   └─────────────────────┘
  White blobs                Outlines (contours)
```

---

## Finding Contours

```python
import cv2
import numpy as np

img = cv2.imread("parking_lot.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Step 1: Create a binary image (threshold or edge detection)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
_, binary = cv2.threshold(blurred, 127, 255, cv2.THRESH_BINARY)

# Step 2: Find contours
contours, hierarchy = cv2.findContours(
    binary,
    cv2.RETR_EXTERNAL,      # retrieval mode
    cv2.CHAIN_APPROX_SIMPLE # approximation method
)

print(f"Found {len(contours)} contours")

# Step 3: Draw contours on the original image
annotated = img.copy()
cv2.drawContours(annotated, contours, -1, (0, 255, 0), 2)
#                                     -1 = draw all    color    thickness

cv2.imshow("Contours", annotated)
cv2.waitKey(0)
```

---

## Retrieval Modes

```python
# RETR_EXTERNAL — only outermost contours (ignore holes)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# RETR_LIST — all contours, no hierarchy (flat list)
contours, _ = cv2.findContours(binary, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

# RETR_TREE — full hierarchy (parent-child relationships)
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
```

For parking detection, `RETR_EXTERNAL` is usually what you want — you care about the outer boundary of objects, not holes inside them.

---

## Approximation Methods

```python
# CHAIN_APPROX_NONE — stores ALL boundary points (memory heavy)
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

# CHAIN_APPROX_SIMPLE — compresses straight segments (stores only endpoints)
# A rectangle stores 4 points instead of hundreds
contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
```

Always use `CHAIN_APPROX_SIMPLE` unless you specifically need every single point.

---

## Contour Properties

Each contour is a NumPy array of shape `(N, 1, 2)` — N points, each with (x, y):

```python
for i, contour in enumerate(contours):
    # Area
    area = cv2.contourArea(contour)
    
    # Perimeter (arc length)
    perimeter = cv2.arcLength(contour, closed=True)
    
    # Bounding rectangle (axis-aligned)
    x, y, w, h = cv2.boundingRect(contour)
    
    # Minimum enclosing circle
    (cx, cy), radius = cv2.minEnclosingCircle(contour)
    
    # Centroid (center of mass)
    M = cv2.moments(contour)
    if M["m00"] != 0:
        centroid_x = int(M["m10"] / M["m00"])
        centroid_y = int(M["m01"] / M["m00"])
    
    # Aspect ratio
    aspect_ratio = float(w) / h if h > 0 else 0
    
    # Extent (ratio of contour area to bounding rect area)
    rect_area = w * h
    extent = area / rect_area if rect_area > 0 else 0
    
    print(f"Contour {i}: area={area:.0f}, aspect={aspect_ratio:.2f}, extent={extent:.2f}")
```

---

## Filtering Contours by Size

Most contours are noise — tiny blobs that aren't cars. Filter by area:

```python
def find_car_contours(binary, min_area=500, max_area=50000):
    """Find contours that could be cars (filter by size)."""
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    car_contours = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area < area < max_area:
            car_contours.append(contour)
    
    return car_contours


# Use it
binary = get_binary_image(frame)  # from thresholding or edge detection
cars = find_car_contours(binary)
print(f"Found {len(cars)} potential cars")
```

---

## Bounding Boxes: What Raj Wants

```python
def detect_objects(frame, min_area=500):
    """Detect objects and return bounding boxes."""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    detections = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < min_area:
            continue
        
        x, y, w, h = cv2.boundingRect(contour)
        detections.append({
            "bbox": (x, y, w, h),
            "area": area,
            "centroid": (x + w // 2, y + h // 2),
        })
    
    return detections


# Visualize
frame = cv2.imread("parking_lot.jpg")
detections = detect_objects(frame)

annotated = frame.copy()
for det in detections:
    x, y, w, h = det["bbox"]
    cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv2.circle(annotated, det["centroid"], 4, (0, 0, 255), -1)
    cv2.putText(annotated, f"A={det['area']}", (x, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)

cv2.imshow("Detections", annotated)
cv2.waitKey(0)
```

---

## Rotated Bounding Box

Cars aren't always axis-aligned. A rotated bounding box fits tighter:

```python
for contour in car_contours:
    # Minimum area rotated rectangle
    rect = cv2.minAreaRect(contour)
    # rect = ((center_x, center_y), (width, height), angle)
    
    # Get the 4 corner points
    box = cv2.boxPoints(rect)
    box = np.int32(box)
    
    # Draw it
    cv2.drawContours(annotated, [box], 0, (0, 0, 255), 2)
```

---

## Contour Approximation (Shape Simplification)

Reduce a complex contour to fewer points (useful for shape classification):

```python
for contour in contours:
    # Approximate the contour with fewer points
    epsilon = 0.02 * cv2.arcLength(contour, True)  # 2% of perimeter
    approx = cv2.approxPolyDP(contour, epsilon, True)
    
    num_vertices = len(approx)
    
    if num_vertices == 3:
        shape = "triangle"
    elif num_vertices == 4:
        shape = "rectangle"
    elif num_vertices > 8:
        shape = "circle-ish"
    else:
        shape = f"{num_vertices}-gon"
    
    # Draw with label
    x, y, w, h = cv2.boundingRect(contour)
    cv2.drawContours(annotated, [approx], 0, (255, 0, 0), 2)
    cv2.putText(annotated, shape, (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)
```

---

## Convex Hull

The convex hull is the smallest convex shape that contains the contour (like stretching a rubber band around it):

```python
for contour in car_contours:
    hull = cv2.convexHull(contour)
    cv2.drawContours(annotated, [hull], 0, (255, 255, 0), 2)
    
    # Convexity defects — where the contour dips inward
    # Useful for detecting complex shapes
    hull_indices = cv2.convexHull(contour, returnPoints=False)
    if len(hull_indices) > 3 and len(contour) > 3:
        defects = cv2.convexityDefects(contour, hull_indices)
```

---

## Practical: Improved Parking Detector with Contours

```python
def parking_detector_v4(frame, spots):
    """
    v4: Uses contours to detect objects in parking spots.
    Returns list of spot statuses with confidence.
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    results = []
    
    for spot in spots:
        y1, y2, x1, x2 = spot["roi"]
        roi = blurred[y1:y2, x1:x2]
        
        # Adaptive threshold (handles varying lighting per spot)
        binary = cv2.adaptiveThreshold(
            roi, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 25, 5
        )
        
        # Find contours in this spot
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Calculate total contour area relative to spot size
        spot_area = (y2 - y1) * (x2 - x1)
        total_contour_area = sum(cv2.contourArea(c) for c in contours)
        fill_ratio = total_contour_area / spot_area
        
        # Count significant contours
        significant = [c for c in contours if cv2.contourArea(c) > spot_area * 0.05]
        
        # Decision: occupied if large contours fill significant portion
        occupied = fill_ratio > 0.3 or len(significant) > 2
        confidence = min(fill_ratio / 0.5, 1.0)  # 0.0 to 1.0
        
        results.append({
            "id": spot["id"],
            "occupied": occupied,
            "confidence": confidence,
            "fill_ratio": fill_ratio,
            "num_contours": len(significant),
        })
    
    return results
```

---

## Hierarchy: Parent-Child Relationships

When using `RETR_TREE`, the hierarchy tells you which contours are inside others:

```python
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# hierarchy shape: (1, N, 4)
# For each contour: [next, previous, first_child, parent]
# -1 means "none"

for i, contour in enumerate(contours):
    next_contour = hierarchy[0][i][0]
    prev_contour = hierarchy[0][i][1]
    first_child = hierarchy[0][i][2]
    parent = hierarchy[0][i][3]
    
    if parent == -1:
        print(f"Contour {i}: top-level (no parent)")
    else:
        print(f"Contour {i}: child of contour {parent}")
```

Useful for: detecting license plates (rectangle inside a rectangle), or distinguishing cars from their shadows.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.findContours(binary, mode, method) │ Find shape boundaries
cv2.drawContours(img, contours, idx, color, thick) │ Draw contours
cv2.contourArea(contour)        │ Area enclosed by contour
cv2.arcLength(contour, closed)  │ Perimeter length
cv2.boundingRect(contour)       │ Axis-aligned bounding box (x,y,w,h)
cv2.minAreaRect(contour)        │ Rotated bounding box
cv2.minEnclosingCircle(contour) │ Smallest circle containing contour
cv2.moments(contour)            │ Spatial moments (for centroid)
cv2.approxPolyDP(contour, eps, closed) │ Simplify shape
cv2.convexHull(contour)         │ Convex hull (rubber band)
cv2.boxPoints(rect)             │ 4 corners of rotated rect
RETR_EXTERNAL                   │ Only outermost contours
RETR_TREE                       │ Full parent-child hierarchy
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

The contour detector works, but the binary masks are messy. Small gaps break contours apart. Noise creates tiny false contours. Shadows connect separate objects into one blob.

Sana: "You need morphological operations. Erosion removes noise. Dilation fills gaps. Opening and closing clean up masks before you find contours. It's the difference between 'kind of works' and 'production ready.'"

---

[← Chapter 4: Filtering](chapter-04-filtering.md) | [Chapter 6: Morphology →](chapter-06-morphology.md)
