# Chapter 7: Line Detection — "Find the Painted Lines"

[← Chapter 6: Morphology](chapter-06-morphology.md) | [Chapter 8: Circle Detection →](chapter-08-circles.md)

---

## The Task

Raj: "We've been manually defining spot ROIs. That doesn't scale to 47 cameras. The parking lines are painted on the ground — detect them automatically. If you can find the lines, you can compute the spots."

---

## Hough Line Transform

The Hough transform detects straight lines in an edge image. It works by converting each edge pixel into a set of possible lines (in parameter space), then finding where many pixels agree on the same line.

```python
import cv2
import numpy as np

img = cv2.imread("parking_lot.jpg")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
edges = cv2.Canny(blurred, 50, 150)

# Standard Hough Line Transform
lines = cv2.HoughLines(edges, rho=1, theta=np.pi/180, threshold=150)
#                              rho_resolution  theta_resolution  min_votes

# Draw the lines
annotated = img.copy()
if lines is not None:
    for line in lines:
        rho, theta = line[0]
        # Convert polar to cartesian (two points far apart)
        a = np.cos(theta)
        b = np.sin(theta)
        x0 = a * rho
        y0 = b * rho
        x1 = int(x0 + 1000 * (-b))
        y1 = int(y0 + 1000 * (a))
        x2 = int(x0 - 1000 * (-b))
        y2 = int(y0 - 1000 * (a))
        cv2.line(annotated, (x1, y1), (x2, y2), (0, 0, 255), 2)

print(f"Found {len(lines) if lines is not None else 0} lines")
cv2.imshow("Hough Lines", annotated)
cv2.waitKey(0)
```

### Parameters

- `rho` → distance resolution in pixels (1 = 1 pixel precision)
- `theta` → angle resolution in radians (π/180 = 1 degree precision)
- `threshold` → minimum number of votes (edge pixels) to count as a line

Higher threshold = fewer lines (only strong ones). Lower = more lines (including noise).

---

## Probabilistic Hough Transform (Better)

The standard Hough gives infinite lines. The probabilistic version gives line **segments** with start and end points:

```python
# Probabilistic Hough — returns line segments (much more useful)
lines = cv2.HoughLinesP(
    edges,
    rho=1,
    theta=np.pi/180,
    threshold=50,
    minLineLength=100,   # ignore short segments
    maxLineGap=10        # connect segments with small gaps
)

annotated = img.copy()
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

print(f"Found {len(lines) if lines is not None else 0} line segments")
cv2.imshow("HoughLinesP", annotated)
cv2.waitKey(0)
```

### Key Parameters

- `minLineLength` → segments shorter than this are rejected
- `maxLineGap` → segments with gaps smaller than this are merged

For parking lines: lines are long (minLineLength=80+) and continuous (maxLineGap=10-20).

---

## Filtering Lines by Angle

Parking lines are typically vertical or near-vertical (from the camera's perspective). Filter out horizontal lines:

```python
def filter_lines_by_angle(lines, min_angle=60, max_angle=120):
    """Keep only lines within an angle range (degrees from horizontal)."""
    filtered = []
    
    if lines is None:
        return filtered
    
    for line in lines:
        x1, y1, x2, y2 = line[0]
        
        # Calculate angle
        dx = x2 - x1
        dy = y2 - y1
        angle = np.degrees(np.arctan2(abs(dy), abs(dx)))
        
        if min_angle <= angle <= max_angle:
            filtered.append(line[0])
    
    return filtered


# Get only near-vertical lines (parking spot dividers)
vertical_lines = filter_lines_by_angle(lines, min_angle=70, max_angle=110)

# Get only near-horizontal lines (row separators)
horizontal_lines = filter_lines_by_angle(lines, min_angle=0, max_angle=20)
```

---

## Detecting Parking Lines Specifically

Parking lines are white or yellow paint on dark asphalt. Use color filtering BEFORE edge detection:

```python
def detect_parking_lines(frame):
    """
    Detect painted parking lines using color + Hough.
    """
    # Step 1: Isolate white/yellow paint
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # White paint: high value, low saturation
    lower_white = np.array([0, 0, 180])
    upper_white = np.array([179, 40, 255])
    white_mask = cv2.inRange(hsv, lower_white, upper_white)
    
    # Yellow paint: specific hue range
    lower_yellow = np.array([15, 80, 150])
    upper_yellow = np.array([35, 255, 255])
    yellow_mask = cv2.inRange(hsv, lower_yellow, upper_yellow)
    
    # Combine
    paint_mask = cv2.bitwise_or(white_mask, yellow_mask)
    
    # Step 2: Clean up with morphology
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    paint_mask = cv2.morphologyEx(paint_mask, cv2.MORPH_CLOSE, kernel)
    paint_mask = cv2.morphologyEx(paint_mask, cv2.MORPH_OPEN, kernel)
    
    # Step 3: Edge detection on the paint mask
    edges = cv2.Canny(paint_mask, 50, 150)
    
    # Step 4: Hough line detection
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=40,
        minLineLength=60,
        maxLineGap=15
    )
    
    return lines, paint_mask


# Use it
lines, mask = detect_parking_lines(frame)

annotated = frame.copy()
if lines is not None:
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)

cv2.imshow("Parking Lines", annotated)
cv2.imshow("Paint Mask", mask)
cv2.waitKey(0)
```

---

## From Lines to Spots: Computing ROIs

Once you have the vertical divider lines, you can compute spot regions between them:

```python
def lines_to_spots(lines, frame_height, row_y1, row_y2):
    """
    Convert detected vertical lines into parking spot ROIs.
    Assumes lines are sorted left-to-right dividers.
    """
    if not lines:
        return []
    
    # Get x-coordinates of vertical lines (use midpoint)
    x_positions = []
    for line in lines:
        x1, y1, x2, y2 = line
        x_mid = (x1 + x2) // 2
        x_positions.append(x_mid)
    
    # Sort left to right
    x_positions.sort()
    
    # Remove duplicates (lines too close together)
    filtered = [x_positions[0]]
    for x in x_positions[1:]:
        if x - filtered[-1] > 30:  # minimum spot width
            filtered.append(x)
    
    # Create spots between consecutive lines
    spots = []
    for i in range(len(filtered) - 1):
        spot = {
            "id": i + 1,
            "roi": (row_y1, row_y2, filtered[i], filtered[i + 1]),
        }
        spots.append(spot)
    
    return spots


# Auto-detect spots
lines, _ = detect_parking_lines(frame)
vertical = filter_lines_by_angle(lines, min_angle=70, max_angle=110)
spots = lines_to_spots(vertical, frame.shape[0], row_y1=200, row_y2=400)

print(f"Auto-detected {len(spots)} parking spots")
```

---

## Dealing with Imperfect Lines

Real parking lots have:
- Faded paint
- Partially occluded lines (cars parked on them)
- Curved lines (perspective distortion)
- Multiple rows at different angles

```python
def merge_similar_lines(lines, distance_threshold=20, angle_threshold=10):
    """Merge lines that are close together and similar angle."""
    if not lines:
        return []
    
    merged = []
    used = [False] * len(lines)
    
    for i in range(len(lines)):
        if used[i]:
            continue
        
        group = [lines[i]]
        used[i] = True
        
        x1_i, y1_i, x2_i, y2_i = lines[i]
        angle_i = np.degrees(np.arctan2(y2_i - y1_i, x2_i - x1_i))
        mid_x_i = (x1_i + x2_i) / 2
        
        for j in range(i + 1, len(lines)):
            if used[j]:
                continue
            
            x1_j, y1_j, x2_j, y2_j = lines[j]
            angle_j = np.degrees(np.arctan2(y2_j - y1_j, x2_j - x1_j))
            mid_x_j = (x1_j + x2_j) / 2
            
            # Similar angle and close together?
            if (abs(angle_i - angle_j) < angle_threshold and
                abs(mid_x_i - mid_x_j) < distance_threshold):
                group.append(lines[j])
                used[j] = True
        
        # Average the group into one line
        avg_line = np.mean(group, axis=0).astype(int)
        merged.append(avg_line)
    
    return merged
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.HoughLines(edges, ρ, θ, thresh) │ Detect infinite lines (polar coords)
cv2.HoughLinesP(edges, ρ, θ, thresh, minLen, maxGap) │ Detect line segments
rho=1, theta=np.pi/180         │ Standard resolution (1px, 1°)
minLineLength                   │ Reject short segments
maxLineGap                      │ Bridge small gaps
np.arctan2(dy, dx)              │ Angle of a line segment
Filter by angle                 │ Keep only vertical/horizontal lines
Color mask → edges → Hough      │ Pipeline for painted lines
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Lines are straight. But some parking lot features are round — wheel stops, circular signs, camera lens artifacts. And Raj wants to detect the round "P" parking signs at lot entrances.

That's the Hough Circle Transform.

---

[← Chapter 6: Morphology](chapter-06-morphology.md) | [Chapter 8: Circle Detection →](chapter-08-circles.md)
