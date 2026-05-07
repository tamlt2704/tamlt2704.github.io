# Chapter 12: Background Subtraction — "What Changed?"

[← Chapter 11: Video Processing](chapter-11-video.md) | [Chapter 13: Object Tracking →](chapter-13-tracking.md)

---

## The Idea

Instead of analyzing each frame in isolation, compare it to what the scene looks like when it's empty. Anything different = something new (a car, a person, a shadow).

Sana: "Background subtraction is the most powerful tool for static cameras. The camera doesn't move. The background doesn't change (much). Only the foreground — cars arriving and leaving — changes. Subtract the background, and you're left with just the interesting stuff."

---

## Simple Subtraction (Naive Approach)

```python
import cv2
import numpy as np

# Take a reference frame (empty lot)
cap = cv2.VideoCapture("parking_lot_video.mp4")
ret, background = cap.read()
background_gray = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
background_gray = cv2.GaussianBlur(background_gray, (5, 5), 0)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Subtract background
    diff = cv2.absdiff(gray, background_gray)
    
    # Threshold the difference
    _, mask = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)
    
    # Clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    cv2.imshow("Frame", frame)
    cv2.imshow("Foreground Mask", mask)
    
    if cv2.waitKey(30) & 0xFF == 27:
        break

cap.release()
```

**Problem:** This breaks when lighting changes. The "background" from 8 AM doesn't match the scene at 2 PM. You need an adaptive background model.

---

## MOG2: Adaptive Background Subtraction

MOG2 (Mixture of Gaussians) maintains a statistical model of the background that adapts over time:

```python
# Create background subtractor
bg_subtractor = cv2.createBackgroundSubtractorMOG2(
    history=500,          # frames used to build background model
    varThreshold=16,      # threshold for foreground detection
    detectShadows=True    # detect shadows (marks them gray)
)

cap = cv2.VideoCapture("parking_lot_video.mp4")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Apply background subtraction
    fg_mask = bg_subtractor.apply(frame)
    
    # fg_mask values:
    # 255 = definite foreground
    # 127 = shadow (if detectShadows=True)
    # 0   = background
    
    # Remove shadows (keep only definite foreground)
    _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
    
    # Clean up
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
    fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
    
    # Find foreground objects
    contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    annotated = frame.copy()
    for contour in contours:
        area = cv2.contourArea(contour)
        if area > 500:  # ignore small noise
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    cv2.imshow("Feed", annotated)
    cv2.imshow("Foreground", fg_mask)
    
    if cv2.waitKey(30) & 0xFF == 27:
        break

cap.release()
```

---

## KNN Background Subtractor

An alternative to MOG2 — sometimes better for outdoor scenes:

```python
bg_subtractor = cv2.createBackgroundSubtractorKNN(
    history=500,
    dist2Threshold=400,    # threshold for foreground
    detectShadows=True
)

# Usage is identical to MOG2
fg_mask = bg_subtractor.apply(frame)
```

**MOG2 vs KNN:**
- MOG2: faster, better for scenes with gradual lighting changes
- KNN: better for scenes with sudden changes, handles multi-modal backgrounds

---

## Learning Rate: How Fast the Background Adapts

```python
# Default learning rate (auto)
fg_mask = bg_subtractor.apply(frame)

# Custom learning rate
fg_mask = bg_subtractor.apply(frame, learningRate=0.01)
# 0 = never update background (static reference)
# 1 = every frame replaces background completely
# 0.001-0.01 = slow adaptation (good for parking lots)
# -1 = automatic (default)
```

For parking lots:
- **Slow learning rate (0.001):** Cars that park for a long time eventually become "background." This is actually useful — you only detect CHANGES.
- **Fast learning rate (0.1):** Adapts quickly to lighting changes but also absorbs parked cars into the background too fast.

---

## Practical: Arrival/Departure Detection

```python
class ArrivalDepartureDetector:
    """
    Detect when cars arrive at or depart from parking spots.
    Uses background subtraction to detect changes.
    """
    
    def __init__(self, spots):
        self.spots = spots
        self.bg_subtractor = cv2.createBackgroundSubtractorMOG2(
            history=1000,
            varThreshold=25,
            detectShadows=True
        )
        self.spot_states = {}  # spot_id → "empty" | "occupied"
        self.change_cooldown = {}  # prevent rapid toggling
        self.warmup_frames = 100  # let background model stabilize
        self.frame_count = 0
    
    def process_frame(self, frame):
        """Process one frame. Returns list of events."""
        self.frame_count += 1
        events = []
        
        # Apply background subtraction
        fg_mask = self.bg_subtractor.apply(frame, learningRate=0.002)
        _, fg_mask = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        
        # Clean up
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Skip during warmup
        if self.frame_count < self.warmup_frames:
            return events
        
        # Check each spot
        for spot in self.spots:
            y1, y2, x1, x2 = spot["roi"]
            spot_mask = fg_mask[y1:y2, x1:x2]
            
            # How much of this spot has foreground activity?
            activity = cv2.countNonZero(spot_mask) / spot_mask.size
            
            # Determine current state
            current_state = "changing" if activity > 0.15 else self.spot_states.get(spot["id"], "empty")
            
            # Detect state transitions
            prev_state = self.spot_states.get(spot["id"])
            if prev_state and current_state != prev_state and current_state != "changing":
                # Check cooldown
                last_change = self.change_cooldown.get(spot["id"], 0)
                if self.frame_count - last_change > 30:  # 1 second at 30fps
                    events.append({
                        "type": "arrival" if current_state == "occupied" else "departure",
                        "spot_id": spot["id"],
                        "frame": self.frame_count,
                    })
                    self.change_cooldown[spot["id"]] = self.frame_count
            
            self.spot_states[spot["id"]] = current_state
        
        return events
```

---

## Shadow Detection and Removal

MOG2 can detect shadows (gray pixels in the mask), but sometimes you need more control:

```python
def remove_shadows_hsv(frame, fg_mask):
    """
    Remove shadow pixels from foreground mask using HSV analysis.
    Shadows are darker but have similar hue to the background.
    """
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Shadow characteristics:
    # - Lower value (darker)
    # - Similar hue to background
    # - Lower saturation
    
    h, s, v = cv2.split(hsv)
    
    # Pixels that are dark AND low saturation are likely shadows
    shadow_mask = cv2.inRange(hsv, 
                              np.array([0, 0, 30]),    # dark
                              np.array([179, 80, 150])) # low saturation, medium brightness
    
    # Remove shadow pixels from foreground mask
    cleaned = cv2.bitwise_and(fg_mask, cv2.bitwise_not(shadow_mask))
    
    return cleaned
```

---

## Getting the Background Image

```python
# After the model has learned, you can extract the background
background = bg_subtractor.getBackgroundImage()

if background is not None:
    cv2.imshow("Learned Background", background)
    cv2.imwrite("empty_lot_reference.jpg", background)
```

This gives you what the lot looks like without any cars — useful for comparison and calibration.

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.createBackgroundSubtractorMOG2(...) │ Gaussian mixture background model
cv2.createBackgroundSubtractorKNN(...)  │ KNN-based background model
bg_sub.apply(frame)             │ Get foreground mask (255=fg, 0=bg)
bg_sub.apply(frame, learningRate=0.01) │ Control adaptation speed
bg_sub.getBackgroundImage()     │ Extract the learned background
detectShadows=True              │ Mark shadows as gray (127)
history=500                     │ Frames used for background model
cv2.absdiff(frame, reference)   │ Simple frame difference
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

Background subtraction tells you THAT something changed. But it doesn't tell you WHERE it went. A car enters the frame, parks, and the foreground mask shows activity. But if you want to follow that car across frames — track its path from entrance to parking spot — you need object tracking.

Raj: "I want to see the path each car takes. Entry point → which spot they chose. That's data I can sell."

---

[← Chapter 11: Video Processing](chapter-11-video.md) | [Chapter 13: Object Tracking →](chapter-13-tracking.md)
