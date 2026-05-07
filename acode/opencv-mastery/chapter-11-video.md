# Chapter 11: Video Processing — "Process the Live Feed"

[← Chapter 10: Template Matching](chapter-10-matching.md) | [Chapter 12: Background Subtraction →](chapter-12-background-subtraction.md)

---

## The Task

Raj: "Enough with static images. Camera 3 streams at 30 fps. I need real-time parking status. Hook up to the feed and process it live."

---

## VideoCapture: Reading Video

```python
import cv2
import time

# From a file
cap = cv2.VideoCapture("parking_lot_video.mp4")

# From a webcam (index 0 = default camera)
# cap = cv2.VideoCapture(0)

# From an RTSP stream (IP camera)
# cap = cv2.VideoCapture("rtsp://admin:password@192.168.1.100:554/stream")

if not cap.isOpened():
    raise RuntimeError("Cannot open video source")

# Get video properties
fps = cap.get(cv2.CAP_PROP_FPS)
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"Video: {width}x{height} @ {fps} fps, {total_frames} frames")
```

---

## The Frame Loop

The fundamental pattern for video processing:

```python
while True:
    ret, frame = cap.read()
    
    if not ret:
        break  # end of video or stream error
    
    # === YOUR PROCESSING HERE ===
    processed = process_frame(frame)
    # ============================
    
    cv2.imshow("Live Feed", processed)
    
    # Wait 1ms for key press. ESC (27) to quit.
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
```

---

## Measuring FPS

```python
def process_video_with_fps(source):
    """Process video and display real-time FPS."""
    cap = cv2.VideoCapture(source)
    
    prev_time = time.time()
    fps_display = 0
    frame_count = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Your processing
        result = detect_parking_spots(frame)
        
        # Calculate FPS
        frame_count += 1
        current_time = time.time()
        elapsed = current_time - prev_time
        
        if elapsed >= 1.0:  # update FPS every second
            fps_display = frame_count / elapsed
            frame_count = 0
            prev_time = current_time
        
        # Display FPS
        cv2.putText(result, f"FPS: {fps_display:.1f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.imshow("ParkEye", result)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    cap.release()
    cv2.destroyAllWindows()
```

---

## Frame Skipping: When Processing Is Slow

If your detection takes 100ms but frames arrive every 33ms (30 fps), you'll fall behind. Solution: skip frames.

```python
def process_every_nth_frame(source, process_every=5):
    """
    Process every Nth frame. Display all frames but only
    run expensive detection periodically.
    """
    cap = cv2.VideoCapture(source)
    frame_count = 0
    last_result = None  # cache the last detection result
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        if frame_count % process_every == 0:
            # Run expensive detection
            last_result = detect_parking_spots(frame)
        
        # Always display, using cached result for annotation
        display = frame.copy()
        if last_result:
            annotate_frame(display, last_result)
        
        cv2.imshow("ParkEye", display)
        if cv2.waitKey(1) & 0xFF == 27:
            break
    
    cap.release()
```

---

## Writing Video Output

```python
def record_processed_video(input_source, output_path, codec="mp4v"):
    """Process video and save the annotated result."""
    cap = cv2.VideoCapture(input_source)
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # Define the codec and create VideoWriter
    fourcc = cv2.VideoWriter_fourcc(*codec)
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Process
        annotated = process_and_annotate(frame)
        
        # Write to output
        out.write(annotated)
    
    cap.release()
    out.release()
    print(f"Saved to {output_path}")
```

Common codecs:
- `"mp4v"` → MP4 (most compatible)
- `"XVID"` → AVI
- `"MJPG"` → Motion JPEG (large files, fast)

---

## Real-Time Parking Monitor

Putting it all together — a live parking status system:

```python
class ParkingMonitor:
    """Real-time parking lot monitor."""
    
    def __init__(self, source, spots, process_interval=10):
        self.cap = cv2.VideoCapture(source)
        self.spots = spots
        self.process_interval = process_interval  # frames between detections
        self.frame_count = 0
        self.status = {}  # spot_id → occupied/empty
        
        if not self.cap.isOpened():
            raise RuntimeError(f"Cannot open: {source}")
    
    def run(self):
        """Main processing loop."""
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Stream ended or error. Reconnecting...")
                time.sleep(2)
                self.cap.open(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                continue
            
            self.frame_count += 1
            
            # Run detection periodically
            if self.frame_count % self.process_interval == 0:
                self.update_status(frame)
            
            # Always display with current status
            display = self.annotate(frame)
            cv2.imshow("ParkEye Monitor", display)
            
            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                break
            elif key == ord('s'):  # screenshot
                cv2.imwrite(f"screenshot_{self.frame_count}.jpg", display)
        
        self.cap.release()
        cv2.destroyAllWindows()
    
    def update_status(self, frame):
        """Run detection on all spots."""
        for spot in self.spots:
            occupied = is_spot_occupied_v5(frame, spot["roi"])
            self.status[spot["id"]] = occupied
    
    def annotate(self, frame):
        """Draw status overlay on frame."""
        display = frame.copy()
        
        empty_count = 0
        total = len(self.spots)
        
        for spot in self.spots:
            y1, y2, x1, x2 = spot["roi"]
            occupied = self.status.get(spot["id"], False)
            
            if not occupied:
                empty_count += 1
            
            color = (0, 0, 255) if occupied else (0, 255, 0)
            cv2.rectangle(display, (x1, y1), (x2, y2), color, 2)
        
        # Status bar
        cv2.rectangle(display, (0, 0), (300, 40), (0, 0, 0), -1)
        cv2.putText(display, f"Available: {empty_count}/{total}",
                    (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        
        return display


# Run it
spots = [
    {"id": 1, "roi": (300, 400, 100, 250)},
    {"id": 2, "roi": (300, 400, 260, 410)},
    # ...
]

monitor = ParkingMonitor("rtsp://camera3.parkeye.local/stream", spots)
monitor.run()
```

---

## Handling Stream Disconnections

IP cameras drop connections. Your code needs to handle this:

```python
def resilient_capture(source, max_retries=5, retry_delay=3):
    """VideoCapture with automatic reconnection."""
    cap = cv2.VideoCapture(source)
    retries = 0
    
    while True:
        ret, frame = cap.read()
        
        if ret:
            retries = 0  # reset on success
            yield frame
        else:
            retries += 1
            print(f"Frame read failed. Retry {retries}/{max_retries}")
            
            if retries >= max_retries:
                print("Max retries reached. Reconnecting...")
                cap.release()
                time.sleep(retry_delay)
                cap = cv2.VideoCapture(source)
                retries = 0
            else:
                time.sleep(0.1)
    
    cap.release()


# Usage
for frame in resilient_capture("rtsp://camera3.local/stream"):
    processed = process_frame(frame)
    cv2.imshow("Feed", processed)
    if cv2.waitKey(1) & 0xFF == 27:
        break
```

---

## Video Properties Reference

```python
# Read properties
fps = cap.get(cv2.CAP_PROP_FPS)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
current_frame = cap.get(cv2.CAP_PROP_POS_FRAMES)
current_ms = cap.get(cv2.CAP_PROP_POS_MSEC)

# Set properties (seek)
cap.set(cv2.CAP_PROP_POS_FRAMES, 100)  # jump to frame 100
cap.set(cv2.CAP_PROP_POS_MSEC, 5000)   # jump to 5 seconds
```

---

## Quick Reference

```
────────────────────────────────┬──────────────────────────────────────
Function                        │ What It Does
────────────────────────────────┼──────────────────────────────────────
cv2.VideoCapture(source)        │ Open video/camera/stream
cap.read()                      │ Get next frame (ret, frame)
cap.isOpened()                  │ Check if source is valid
cap.release()                   │ Close the video source
cap.get(PROP) / cap.set(PROP)   │ Read/write video properties
cv2.VideoWriter(path, fourcc, fps, size) │ Write video to file
cv2.VideoWriter_fourcc(*codec)  │ Define codec (mp4v, XVID, MJPG)
cv2.waitKey(1) & 0xFF          │ Check for key press (1ms delay)
Frame skipping                  │ Process every Nth frame for speed
────────────────────────────────┴──────────────────────────────────────
```

---

## What's Next

You're processing live video. But your detection still analyzes each frame independently — it doesn't know what the lot looked like 5 seconds ago. If you had a reference image of the empty lot, you could simply subtract it from the current frame to see what's new.

Sana: "Background subtraction. Maintain a model of the 'empty' scene. Anything that differs from the background is foreground — a car that arrived, a person walking, a shadow that moved."

---

[← Chapter 10: Template Matching](chapter-10-matching.md) | [Chapter 12: Background Subtraction →](chapter-12-background-subtraction.md)
