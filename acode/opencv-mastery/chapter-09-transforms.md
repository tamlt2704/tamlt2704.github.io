# Chapter 9: Geometric Transforms — "The Camera Is Tilted"

[← Chapter 8: Circle Detection](chapter-08-circles.md) | [Chapter 10: Template Matching →](chapter-10-matching.md)

---

## The Problem

Camera 7 is mounted at an angle. Camera 12 looks down at the lot from a pole, creating perspective distortion — spots near the camera look huge, spots far away look tiny. Your detectors assume a flat, top-down view.

Sana: "Warp the image. Pick four points on the ground (corners of a known rectangle — like a parking spot), and transform the image so those points become a proper rectangle. Now everything is normalized."

---

## Rotation

The simplest transform — rotate the image by an angle:

```python
import cv2
import numpy as np

img = cv2.imread("tilted_camera.jpg")
h, w = img.shape[:2]

# Rotation matrix: center, angle (degrees), scale
center = (w // 2, h // 2)
angle = 15  # degrees counter-clockwise
scale = 1.0

M = cv2.getRotationMatrix2D(center, angle, scale)

# Apply rotation
rotated = cv2.warpAffine(img, M, (w, h))

cv2.imshow("Original", img)
cv2.imshow("Rotated 15°", rotated)
cv2.waitKey(0)
```

Problem: rotation can crop corners. To keep the full image:

```python
def rotate_full(img, angle):
    """Rotate without cropping — expands the canvas."""
    h, w = img.shape[:2]
    center = (w // 2, h // 2)
    
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Calculate new bounding box size
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    new_w = int(h * sin + w * cos)
    new_h = int(h * cos + w * sin)
    
    # Adjust the rotation matrix for the new center
    M[0, 2] += (new_w - w) / 2
    M[1, 2] += (new_h - h) / 2
    
    return cv2.warpAffine(img, M, (new_w, new_h))
```

---

## Affine Transform

An affine transform preserves parallel lines. It can rotate, scale, shear, and translate — but not change perspective.

Defined by 3 point correspondences (where 3 points move to):

```python
# Define 3 source points and where they should map to
src_points = np.float32([[50, 50], [200, 50], [50, 200]])
dst_points = np.float32([[10, 100], [200, 50], [100, 250]])

# Compute the affine matrix
M = cv2.getAffineTransform(src_points, dst_points)

# Apply
transformed = cv2.warpAffine(img, M, (w, h))
```

---

## Perspective Transform (The Important One)

Perspective transform handles the camera's viewpoint distortion. It maps any quadrilateral to any other quadrilateral — including turning a trapezoid (perspective view) into a rectangle (top-down view).

Defined by 4 point correspondences:

```python
def perspective_correction(img, src_points, dst_width, dst_height):
    """
    Warp a quadrilateral region to a rectangle.
    
    src_points: 4 corners in the source image (what you see)
    dst_width/height: desired output size
    """
    src = np.float32(src_points)
    dst = np.float32([
        [0, 0],
        [dst_width, 0],
        [dst_width, dst_height],
        [0, dst_height]
    ])
    
    # Compute perspective transform matrix
    M = cv2.getPerspectiveTransform(src, dst)
    
    # Apply
    warped = cv2.warpPerspective(img, M, (dst_width, dst_height))
    
    return warped, M


# Example: straighten a parking spot viewed at an angle
# These are the 4 corners of a parking spot in the camera image
spot_corners = [
    [120, 200],   # top-left
    [280, 180],   # top-right (perspective makes it higher)
    [300, 350],   # bottom-right
    [100, 370],   # bottom-left
]

# Warp to a standard rectangle
warped_spot, M = perspective_correction(img, spot_corners, 200, 400)

cv2.imshow("Original view", img)
cv2.imshow("Top-down view", warped_spot)
cv2.waitKey(0)
```

---

## Bird's Eye View: The Parking Lot from Above

The killer application for ParkEye — transform the angled camera view into a top-down map:

```python
def create_birds_eye_view(frame, ground_corners, output_size=(800, 600)):
    """
    Transform camera view to bird's eye (top-down) view.
    
    ground_corners: 4 points on the ground plane in camera image
                    (e.g., corners of the parking lot area)
    output_size: (width, height) of the output image
    """
    src = np.float32(ground_corners)
    dst = np.float32([
        [0, 0],
        [output_size[0], 0],
        [output_size[0], output_size[1]],
        [0, output_size[1]]
    ])
    
    M = cv2.getPerspectiveTransform(src, dst)
    birds_eye = cv2.warpPerspective(frame, M, output_size)
    
    return birds_eye, M


# Define the ground plane corners (calibrated once per camera)
# These are 4 points you know form a rectangle on the ground
ground_corners = [
    [150, 300],   # top-left of lot (in camera image)
    [1750, 280],  # top-right
    [1900, 900],  # bottom-right
    [20, 920],    # bottom-left
]

birds_eye, M = create_birds_eye_view(frame, ground_corners)
cv2.imshow("Bird's Eye View", birds_eye)
cv2.waitKey(0)
```

In the bird's eye view:
- All parking spots are the same size
- Lines are straight and parallel
- Detection algorithms work uniformly
- You can measure real-world distances

---

## Inverse Transform: Map Detections Back

After detecting in the warped view, map coordinates back to the original:

```python
def transform_point(point, M):
    """Transform a single point using a perspective matrix."""
    pt = np.array([[[point[0], point[1]]]], dtype=np.float32)
    transformed = cv2.perspectiveTransform(pt, M)
    return int(transformed[0][0][0]), int(transformed[0][0][1])


def transform_points_inverse(points, M):
    """Transform points from warped space back to original."""
    M_inv = np.linalg.inv(M)
    results = []
    for pt in points:
        results.append(transform_point(pt, M_inv))
    return results
```

---

## Flipping and Transposing

Simple transforms that don't need matrices:

```python
# Flip horizontally (mirror)
flipped_h = cv2.flip(img, 1)

# Flip vertically
flipped_v = cv2.flip(img, 0)

# Flip both (180° rotation)
flipped_both = cv2.flip(img, -1)

# Transpose (swap rows and columns)
transposed = cv2.transpose(img)
```

---

## Translation (Shifting)

```python
def translate(img, tx, ty):
    """Shift image by (tx, ty) pixels."""
    M = np.float32([[1, 0, tx], [0, 1, ty]])
    return cv2.warpAffine(img, M, (img.shape[1], img.shape[0]))

# Shift 50px right, 30px down
shifted = translate(img, 50, 30)
```

---

## Practical: Camera Calibration for ParkEye

Each camera needs a one-time calibration to define the perspective transform:

```python
class CameraCalibration:
    """
    One-time calibration for a parking lot camera.
    Stores the perspective transform for bird's eye conversion.
    """
    
    def __init__(self, camera_id):
        self.camera_id = camera_id
        self.M = None
        self.M_inv = None
        self.output_size = None
    
    def calibrate(self, frame, ground_corners, output_size=(800, 600)):
        """
        Calibrate using 4 known ground points.
        Call once during setup, save the result.
        """
        self.output_size = output_size
        src = np.float32(ground_corners)
        dst = np.float32([
            [0, 0],
            [output_size[0], 0],
            [output_size[0], output_size[1]],
            [0, output_size[1]]
        ])
        
        self.M = cv2.getPerspectiveTransform(src, dst)
        self.M_inv = cv2.getPerspectiveTransform(dst, src)
    
    def to_birds_eye(self, frame):
        """Convert camera frame to bird's eye view."""
        return cv2.warpPerspective(frame, self.M, self.output_size)
    
    def to_camera_view(self, point):
        """Convert bird's eye coordinate back to camera coordinate."""
        pt = np.array([[[point[0], point[1]]]], dtype=np.float32)
        result = cv2.perspectiveTransform(pt, self.M_inv)
        return int(result[0][0][0]), int(result[0][0][1])
    
    def save(self, path):
        """Save calibration to file."""
        np.savez(path, M=self.M, M_inv=self.M_inv, output_size=self.output_size)
    
    def load(self, path):
        """Load calibration from file."""
        data = np.load(path)
        self.M = data["M"]
        self.M_inv = data["M_inv"]
        self.output_size = tuple(data["output_size"])


# Usage
cam7 = CameraCalibration(camera_id=7)
cam7.calibrate(frame, ground_corners=[[150, 300], [1750, 280], [1900, 900], [20, 920]])
cam7.save("calibrations/camera_7.npz")

# In production
cam7.load("calibrations/camera_7.npz")
birds_eye = cam7.to_birds_eye(frame)
# Now run detection on birds_eye...
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.getRotationMatrix2D(c, θ, s)│ 2×3 rotation matrix
cv2.warpAffine(img, M, size)    │ Apply affine transform (3 points)
cv2.getAffineTransform(src, dst)│ Compute affine from 3 point pairs
cv2.getPerspectiveTransform(src, dst) │ Compute perspective from 4 points
cv2.warpPerspective(img, M, size) │ Apply perspective transform
cv2.perspectiveTransform(pts, M)│ Transform points (not image)
cv2.flip(img, code)             │ Mirror (1=horiz, 0=vert, -1=both)
np.linalg.inv(M)                │ Inverse matrix (for reverse mapping)
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You can now normalize any camera's view. But what about recognizing specific things — like a particular sign template, or matching a known license plate format? 

Raj: "I have an image of the 'No Parking' sign. Find every instance of it in the camera feed."

That's template matching and feature matching.

---

[← Chapter 8: Circle Detection](chapter-08-circles.md) | [Chapter 10: Template Matching →](chapter-10-matching.md)
