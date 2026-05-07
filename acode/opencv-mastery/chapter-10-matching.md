# Chapter 10: Template & Feature Matching — "Find This Thing"

[← Chapter 9: Geometric Transforms](chapter-09-transforms.md) | [Chapter 11: Video Processing →](chapter-11-video.md)

---

## The Task

Raj: "I have an image of our company logo on the parking signs. Find every sign in the camera feed. Also — can you match a known license plate format?"

---

## Template Matching

Template matching slides a small image (template) across a larger image and measures how well it matches at each position. It's like a "find this pattern" search.

```python
import cv2
import numpy as np

# Load the scene and the template
scene = cv2.imread("parking_lot.jpg")
template = cv2.imread("no_parking_sign.jpg")

# Convert both to grayscale
scene_gray = cv2.cvtColor(scene, cv2.COLOR_BGR2GRAY)
template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

h, w = template_gray.shape

# Perform template matching
result = cv2.matchTemplate(scene_gray, template_gray, cv2.TM_CCOEFF_NORMED)

# Find the best match location
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

# For TM_CCOEFF_NORMED, best match is the maximum
top_left = max_loc
bottom_right = (top_left[0] + w, top_left[1] + h)

print(f"Best match confidence: {max_val:.3f}")

# Draw bounding box
annotated = scene.copy()
cv2.rectangle(annotated, top_left, bottom_right, (0, 255, 0), 2)
cv2.putText(annotated, f"{max_val:.2f}", (top_left[0], top_left[1] - 10),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

cv2.imshow("Match", annotated)
cv2.waitKey(0)
```

---

## Matching Methods

```python
# Normalized methods (output 0-1, easier to threshold):
cv2.TM_CCOEFF_NORMED   # Best for most cases. 1 = perfect match.
cv2.TM_CCORR_NORMED    # Cross-correlation. Can have false positives.
cv2.TM_SQDIFF_NORMED   # Squared difference. 0 = perfect match (inverted!).

# Non-normalized (raw values, harder to interpret):
cv2.TM_CCOEFF
cv2.TM_CCORR
cv2.TM_SQDIFF
```

**Use `TM_CCOEFF_NORMED`** unless you have a specific reason not to.

---

## Finding Multiple Matches

`minMaxLoc` only gives the single best match. To find all instances:

```python
def find_all_matches(scene_gray, template_gray, threshold=0.8):
    """Find all locations where template matches above threshold."""
    h, w = template_gray.shape
    
    result = cv2.matchTemplate(scene_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    
    # Find all locations above threshold
    locations = np.where(result >= threshold)
    
    # Convert to list of (x, y) points
    matches = []
    for pt in zip(*locations[::-1]):  # switch to (x, y) from (row, col)
        matches.append(pt)
    
    # Non-maximum suppression (remove overlapping detections)
    matches = non_max_suppression(matches, w, h)
    
    return matches


def non_max_suppression(points, w, h, overlap_thresh=0.5):
    """Remove overlapping detections."""
    if not points:
        return []
    
    # Convert to bounding boxes
    boxes = [(x, y, x + w, y + h) for x, y in points]
    
    # Simple NMS: keep only non-overlapping boxes
    kept = []
    for box in boxes:
        overlap = False
        for kept_box in kept:
            # Check if boxes overlap significantly
            x_overlap = max(0, min(box[2], kept_box[2]) - max(box[0], kept_box[0]))
            y_overlap = max(0, min(box[3], kept_box[3]) - max(box[1], kept_box[1]))
            intersection = x_overlap * y_overlap
            area = w * h
            if intersection / area > overlap_thresh:
                overlap = True
                break
        if not overlap:
            kept.append(box)
    
    return [(b[0], b[1]) for b in kept]


# Use it
matches = find_all_matches(scene_gray, template_gray, threshold=0.75)
print(f"Found {len(matches)} instances")

annotated = scene.copy()
for (x, y) in matches:
    cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
```

---

## Limitations of Template Matching

Template matching fails when:
- **Scale changes** — template is a different size than the target
- **Rotation** — target is rotated relative to template
- **Lighting changes** — brightness/contrast differs
- **Partial occlusion** — part of the target is hidden

For these cases, you need **feature matching**.

---

## Feature Matching: Scale and Rotation Invariant

Feature matching finds distinctive keypoints in both images and matches them:

```python
# ORB (Oriented FAST and Rotated BRIEF) — fast, free, good enough
orb = cv2.ORB_create(nfeatures=500)

# Detect keypoints and compute descriptors
kp1, des1 = orb.detectAndCompute(template_gray, None)
kp2, des2 = orb.detectAndCompute(scene_gray, None)

# Match descriptors using Brute-Force matcher
bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
matches = bf.match(des1, des2)

# Sort by distance (best matches first)
matches = sorted(matches, key=lambda x: x.distance)

# Draw top 20 matches
match_img = cv2.drawMatches(
    template, kp1, scene, kp2,
    matches[:20], None,
    flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS
)

cv2.imshow("Feature Matches", match_img)
cv2.waitKey(0)
```

---

## Feature Detectors Comparison

```
Detector │ Speed  │ Rotation │ Scale │ License │ Best For
─────────┼────────┼──────────┼───────┼─────────┼──────────────────
ORB      │ Fast   │ Yes      │ Some  │ Free    │ Real-time, general
SIFT     │ Slow   │ Yes      │ Yes   │ Free*   │ Best accuracy
AKAZE    │ Medium │ Yes      │ Yes   │ Free    │ Good balance
BRISK    │ Fast   │ Yes      │ Yes   │ Free    │ Mobile/embedded
```

*SIFT patent expired in 2020, now free in OpenCV.

```python
# SIFT — best quality (slower)
sift = cv2.SIFT_create()
kp1, des1 = sift.detectAndCompute(template_gray, None)
kp2, des2 = sift.detectAndCompute(scene_gray, None)

# For SIFT/AKAZE, use NORM_L2 (not NORM_HAMMING)
bf = cv2.BFMatcher(cv2.NORM_L2, crossCheck=True)
matches = bf.match(des1, des2)
```

---

## FLANN Matcher (Faster for Large Sets)

```python
# FLANN-based matcher — faster than brute force for many keypoints
FLANN_INDEX_LSH = 6
index_params = dict(algorithm=FLANN_INDEX_LSH, table_number=6, key_size=12, multi_probe_level=1)
search_params = dict(checks=50)

flann = cv2.FlannBasedMatcher(index_params, search_params)
matches = flann.knnMatch(des1, des2, k=2)

# Lowe's ratio test — filter good matches
good_matches = []
for m, n in matches:
    if m.distance < 0.7 * n.distance:
        good_matches.append(m)

print(f"Good matches: {len(good_matches)}")
```

---

## Homography: Find the Object's Exact Position

If you have enough good matches, you can compute a homography — the exact perspective transform that maps the template onto the scene:

```python
def find_object_homography(template_gray, scene_gray, min_matches=10):
    """
    Find an object in a scene using feature matching + homography.
    Returns the bounding polygon in the scene.
    """
    orb = cv2.ORB_create(nfeatures=1000)
    
    kp1, des1 = orb.detectAndCompute(template_gray, None)
    kp2, des2 = orb.detectAndCompute(scene_gray, None)
    
    if des1 is None or des2 is None:
        return None
    
    bf = cv2.BFMatcher(cv2.NORM_HAMMING)
    matches = bf.knnMatch(des1, des2, k=2)
    
    # Ratio test
    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)
    
    if len(good) < min_matches:
        return None
    
    # Extract matched point coordinates
    src_pts = np.float32([kp1[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
    dst_pts = np.float32([kp2[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
    
    # Find homography using RANSAC (robust to outliers)
    M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
    
    if M is None:
        return None
    
    # Transform template corners to scene coordinates
    h, w = template_gray.shape
    corners = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
    scene_corners = cv2.perspectiveTransform(corners, M)
    
    return scene_corners


# Use it
corners = find_object_homography(template_gray, scene_gray)

if corners is not None:
    # Draw the detected object boundary
    annotated = scene.copy()
    corners_int = np.int32(corners)
    cv2.polylines(annotated, [corners_int], True, (0, 255, 0), 3)
    cv2.imshow("Object Found", annotated)
else:
    print("Object not found")
```

---

## Practical: Multi-Scale Template Matching

Since basic template matching doesn't handle scale, search at multiple scales:

```python
def multi_scale_template_match(scene_gray, template_gray, 
                                scales=np.linspace(0.5, 1.5, 20),
                                threshold=0.8):
    """
    Template matching across multiple scales.
    Handles size differences between template and target.
    """
    best_match = None
    best_val = -1
    template_h, template_w = template_gray.shape
    
    for scale in scales:
        # Resize template
        new_w = int(template_w * scale)
        new_h = int(template_h * scale)
        
        if new_w > scene_gray.shape[1] or new_h > scene_gray.shape[0]:
            continue
        if new_w < 10 or new_h < 10:
            continue
        
        resized = cv2.resize(template_gray, (new_w, new_h))
        
        result = cv2.matchTemplate(scene_gray, resized, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val > best_val:
            best_val = max_val
            best_match = (max_loc, new_w, new_h, scale)
    
    if best_match and best_val >= threshold:
        loc, w, h, scale = best_match
        return {
            "location": loc,
            "size": (w, h),
            "scale": scale,
            "confidence": best_val,
        }
    
    return None
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.matchTemplate(scene, tmpl, method) │ Slide template, measure similarity
cv2.TM_CCOEFF_NORMED           │ Best method (1 = perfect match)
cv2.minMaxLoc(result)           │ Find best match location
cv2.ORB_create()                │ Fast feature detector (free)
cv2.SIFT_create()               │ Best feature detector (slower)
orb.detectAndCompute(img, None) │ Find keypoints + descriptors
cv2.BFMatcher(norm, crossCheck) │ Brute-force descriptor matching
cv2.FlannBasedMatcher(...)      │ Fast approximate matching
cv2.findHomography(src, dst, RANSAC) │ Find perspective transform from matches
cv2.perspectiveTransform(pts, M)│ Apply homography to points
Lowe's ratio test (0.7)         │ Filter good matches from noise
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Everything so far has been single-frame analysis. But parking lots are dynamic — cars arrive, park, leave. You need to process video: frame by frame, in real-time, detecting changes over time.

Raj: "Stop analyzing screenshots. Hook up to the live feed. I want real-time status updates."

---

[← Chapter 9: Geometric Transforms](chapter-09-transforms.md) | [Chapter 11: Video Processing →](chapter-11-video.md)
