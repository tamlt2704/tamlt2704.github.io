# Chapter 46: FFmpeg — Master Audio & Video from the Command Line

## What you'll learn

- What FFmpeg is and core concepts (containers, codecs, streams)
- Essential commands: convert, trim, resize, extract audio, merge
- Video encoding: H.264, H.265, VP9, AV1 — quality vs file size
- Audio processing: extract, convert, mix, normalize
- Filters: crop, rotate, speed, overlay, text, fade
- Combining clips: concat, picture-in-picture, side-by-side
- Streaming: HLS, DASH, RTMP
- Automation: batch processing, scripting, Node.js integration
- Performance: hardware acceleration (GPU encoding)

---

## PART 1: Fundamentals

## 46.1 What FFmpeg does

FFmpeg is the Swiss Army knife for audio/video. It can:
- Convert between any format (MP4, MKV, WebM, AVI, MOV, GIF, MP3, FLAC...)
- Trim, cut, merge, split video
- Resize, crop, rotate, add filters
- Extract audio from video
- Encode/transcode (change quality/codec/bitrate)
- Stream (live or on-demand)
- Generate thumbnails, waveforms, spectrograms

```bash
# Install
# macOS:   brew install ffmpeg
# Ubuntu:  sudo apt install ffmpeg
# Windows: download from ffmpeg.org or use choco install ffmpeg

ffmpeg -version
```

## 46.2 Core concepts

```
┌─────────────────────────────────────────────────────┐
│                 VIDEO FILE (container)               │
│                                                     │
│  Container format: .mp4, .mkv, .webm, .avi, .mov   │
│  (just a wrapper — holds streams)                    │
│                                                     │
│  ┌─────────────────┐  ┌─────────────────┐          │
│  │  Video Stream   │  │  Audio Stream   │          │
│  │  Codec: H.264   │  │  Codec: AAC     │          │
│  │  Resolution:    │  │  Sample rate:   │          │
│  │  1920×1080      │  │  48kHz          │          │
│  │  FPS: 30        │  │  Channels: 2    │          │
│  │  Bitrate: 5Mbps │  │  Bitrate: 192k  │          │
│  └─────────────────┘  └─────────────────┘          │
│                                                     │
│  ┌─────────────────┐                               │
│  │  Subtitle Stream │ (optional)                    │
│  │  Format: SRT     │                               │
│  └─────────────────┘                               │
└─────────────────────────────────────────────────────┘
```

**Container** = packaging format (MP4, MKV) — doesn't affect quality
**Codec** = how video/audio is compressed (H.264, AAC) — determines quality + size
**Stream** = one track (video, audio, subtitles) inside the container

| Term | Examples | Controls |
|------|----------|----------|
| Container | .mp4, .mkv, .webm, .avi | Compatibility, features (subtitles, chapters) |
| Video codec | H.264, H.265 (HEVC), VP9, AV1 | Quality per file size, decode speed |
| Audio codec | AAC, Opus, MP3, FLAC | Audio quality, compression |
| Bitrate | 5 Mbps video, 192 kbps audio | Quality vs file size tradeoff |
| Resolution | 1920×1080, 3840×2160 | Detail level |
| Frame rate | 24, 30, 60 fps | Smoothness |

## 46.3 The FFmpeg command structure

```bash
ffmpeg [global options] -i input [input options] [filters] output [output options]

# Simplest form:
ffmpeg -i input.avi output.mp4
# FFmpeg auto-detects formats, picks sensible defaults
```

## 46.4 Inspect a file (ffprobe)

```bash
# Show all stream info
ffprobe -v quiet -show_format -show_streams input.mp4

# Quick summary
ffprobe -v quiet -print_format json -show_format -show_streams input.mp4

# Just duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4
```

---

## PART 2: Essential Commands

## 46.5 Format conversion

```bash
# Convert AVI to MP4
ffmpeg -i input.avi output.mp4

# Convert to WebM (for web)
ffmpeg -i input.mp4 -c:v libvpx-vp9 -crf 30 -b:v 0 -c:a libopus output.webm

# Convert to GIF (no audio)
ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1" -loop 0 output.gif

# MP4 to MP3 (extract audio only)
ffmpeg -i video.mp4 -vn -acodec libmp3lame -q:a 2 audio.mp3

# MOV to MP4 (just remux — no re-encoding, instant)
ffmpeg -i input.mov -c copy output.mp4
```

**`-c copy`** = stream copy (no re-encoding). Instant, no quality loss. Works when input and output formats are compatible.

## 46.6 Trim / Cut

```bash
# Cut from 00:01:30 to 00:03:00 (1.5 min clip)
ffmpeg -i input.mp4 -ss 00:01:30 -to 00:03:00 -c copy output.mp4

# Cut first 30 seconds
ffmpeg -i input.mp4 -t 30 -c copy first30.mp4

# Cut last 60 seconds (seek from end)
ffmpeg -sseof -60 -i input.mp4 -c copy last60.mp4

# ⚠️ -ss BEFORE -i = fast seek (may be inaccurate by a few frames)
# -ss AFTER -i = accurate but slower (decodes from start)

# Accurate cut with re-encoding:
ffmpeg -i input.mp4 -ss 00:01:30 -to 00:03:00 -c:v libx264 -c:a aac output.mp4
```

## 46.7 Resize / Scale

```bash
# Resize to 720p (maintain aspect ratio)
ffmpeg -i input.mp4 -vf "scale=1280:720" output.mp4

# Resize to width 640, auto-calculate height (maintain ratio)
ffmpeg -i input.mp4 -vf "scale=640:-1" output.mp4

# Force even dimensions (required by many codecs)
ffmpeg -i input.mp4 -vf "scale=640:-2" output.mp4

# Scale to fit in 1280×720 box (pad with black bars if needed)
ffmpeg -i input.mp4 -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" output.mp4
```

## 46.8 Audio extraction and conversion

```bash
# Extract audio (keep original codec)
ffmpeg -i video.mp4 -vn -c:a copy audio.aac

# Convert to MP3 (variable bitrate, high quality)
ffmpeg -i input.mp4 -vn -c:a libmp3lame -q:a 0 output.mp3
# -q:a 0 = best quality (~245kbps), -q:a 9 = worst (~65kbps)

# Convert to WAV (uncompressed — for editing)
ffmpeg -i input.mp3 output.wav

# Convert to FLAC (lossless compression)
ffmpeg -i input.wav output.flac

# Convert to Opus (best compression/quality ratio for speech)
ffmpeg -i input.mp3 -c:a libopus -b:a 64k output.opus

# Replace audio in video
ffmpeg -i video.mp4 -i new_audio.mp3 -c:v copy -c:a aac -map 0:v:0 -map 1:a:0 output.mp4

# Remove audio from video
ffmpeg -i input.mp4 -an output_silent.mp4
```

## 46.9 Screenshots and thumbnails

```bash
# Single frame at timestamp
ffmpeg -i input.mp4 -ss 00:00:30 -frames:v 1 thumbnail.jpg

# One thumbnail every 10 seconds
ffmpeg -i input.mp4 -vf "fps=1/10" thumb_%04d.jpg

# Contact sheet (grid of thumbnails)
ffmpeg -i input.mp4 -vf "select=not(mod(n\,300)),scale=320:180,tile=4x4" -frames:v 1 contactsheet.jpg

# Best quality thumbnail (pick most different frame in first 60s)
ffmpeg -i input.mp4 -vf "thumbnail=300" -frames:v 1 best_thumb.jpg
```

---

## PART 3: Encoding — Quality vs Size

## 46.10 H.264 encoding (most compatible)

```bash
# CRF (Constant Rate Factor) — best quality-to-size ratio
# CRF 0 = lossless, 18 = visually lossless, 23 = default, 28 = low quality, 51 = worst
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset medium -c:a aac -b:a 128k output.mp4

# Presets: ultrafast, superfast, veryfast, faster, fast, medium, slow, slower, veryslow
# Slower preset = better compression (smaller file) at same quality, but MUCH longer encode time

# For web delivery (good balance):
ffmpeg -i input.mp4 -c:v libx264 -crf 23 -preset slow -profile:v high -level 4.1 \
    -movflags +faststart -c:a aac -b:a 128k output.mp4
# -movflags +faststart: moves metadata to front (allows streaming before full download)
# -profile:v high -level 4.1: maximum compatibility with browsers/devices
```

## 46.11 H.265/HEVC (50% smaller than H.264 at same quality)

```bash
ffmpeg -i input.mp4 -c:v libx265 -crf 28 -preset medium -c:a aac -b:a 128k output.mp4
# CRF scale is different from H.264: CRF 28 H.265 ≈ CRF 23 H.264 (same quality, smaller file)

# ⚠️ H.265 encoding is 3-10× SLOWER than H.264
# ⚠️ Not supported everywhere (Safari/iOS yes, some older Android no)
```

## 46.12 AV1 (best compression, slowest encoding)

```bash
# AV1 with libaom (very slow but best compression)
ffmpeg -i input.mp4 -c:v libaom-av1 -crf 30 -cpu-used 4 -c:a libopus output.webm

# SVT-AV1 (much faster AV1 encoder)
ffmpeg -i input.mp4 -c:v libsvtav1 -crf 30 -preset 6 -c:a libopus output.webm
# preset 0-13: lower = better quality/size, higher = faster

# AV1 is ~30% smaller than H.265 at same quality
# Used by YouTube, Netflix for efficient streaming
```

## 46.13 Encoding comparison

| Codec | Quality/Size | Encode speed | Compatibility | Use when |
|-------|-------------|-------------|---------------|----------|
| H.264 | Good | Fast | Universal | Maximum compatibility |
| H.265 | Better (50% smaller) | Slow | Most devices | Storage savings, Apple ecosystem |
| VP9 | ≈ H.265 | Slow | Chrome, Firefox, Android | WebM for web |
| AV1 | Best (30% smaller than H.265) | Very slow | Modern browsers, YouTube | Future-proof, streaming at scale |

---

## PART 4: Filters

## 46.14 Video filters (`-vf`)

```bash
# Crop (width:height:x:y — top-left origin)
ffmpeg -i input.mp4 -vf "crop=1280:720:320:180" output.mp4

# Crop center square
ffmpeg -i input.mp4 -vf "crop=min(iw\,ih):min(iw\,ih)" square.mp4

# Rotate
ffmpeg -i input.mp4 -vf "rotate=PI/4" rotated.mp4        # 45 degrees
ffmpeg -i input.mp4 -vf "transpose=1" rotated90.mp4       # 90° clockwise

# Speed up (2×) / slow down (0.5×)
ffmpeg -i input.mp4 -vf "setpts=0.5*PTS" -af "atempo=2.0" fast.mp4
ffmpeg -i input.mp4 -vf "setpts=2.0*PTS" -af "atempo=0.5" slow.mp4

# Add text overlay
ffmpeg -i input.mp4 -vf "drawtext=text='Hello World':fontsize=48:fontcolor=white:x=50:y=50" output.mp4

# Add timestamp
ffmpeg -i input.mp4 -vf "drawtext=text='%{pts\:hms}':fontsize=24:fontcolor=white:x=10:y=10" output.mp4

# Fade in (first 2 seconds) / fade out (last 2 seconds)
ffmpeg -i input.mp4 -vf "fade=t=in:st=0:d=2,fade=t=out:st=58:d=2" output.mp4

# Convert to grayscale
ffmpeg -i input.mp4 -vf "hue=s=0" bw.mp4

# Blur
ffmpeg -i input.mp4 -vf "boxblur=10:5" blurred.mp4

# Sharpen
ffmpeg -i input.mp4 -vf "unsharp=5:5:1.0" sharp.mp4

# Denoise
ffmpeg -i input.mp4 -vf "nlmeans=s=5:p=7:r=15" denoised.mp4

# Chaining filters (comma-separated)
ffmpeg -i input.mp4 -vf "scale=1280:720,crop=1000:600:140:60,drawtext=text='Title':fontsize=36:x=10:y=10" output.mp4
```

## 46.15 Audio filters (`-af`)

```bash
# Volume adjustment
ffmpeg -i input.mp4 -af "volume=2.0" louder.mp4        # 2× louder
ffmpeg -i input.mp4 -af "volume=-10dB" quieter.mp4     # reduce by 10dB

# Normalize audio (consistent loudness)
ffmpeg -i input.mp4 -af "loudnorm=I=-16:LRA=11:TP=-1.5" normalized.mp4

# Fade in/out audio
ffmpeg -i input.mp3 -af "afade=t=in:d=3,afade=t=out:st=57:d=3" faded.mp3

# Remove silence (useful for podcasts)
ffmpeg -i input.mp3 -af "silenceremove=start_periods=1:start_threshold=-50dB" trimmed.mp3

# Change tempo without changing pitch
ffmpeg -i input.mp3 -af "atempo=1.5" faster.mp3

# Mix two audio tracks
ffmpeg -i voice.mp3 -i music.mp3 -filter_complex "amix=inputs=2:duration=first:dropout_transition=2" mixed.mp3
```

---

## PART 5: Combining & Complex Operations

## 46.16 Concatenate (join clips end-to-end)

```bash
# Method 1: concat demuxer (same codec — no re-encoding)
# Create list.txt:
# file 'clip1.mp4'
# file 'clip2.mp4'
# file 'clip3.mp4'
ffmpeg -f concat -safe 0 -i list.txt -c copy output.mp4

# Method 2: filter (different codecs — re-encodes)
ffmpeg -i clip1.mp4 -i clip2.mp4 -i clip3.mp4 \
    -filter_complex "[0:v][0:a][1:v][1:a][2:v][2:a]concat=n=3:v=1:a=1[outv][outa]" \
    -map "[outv]" -map "[outa]" output.mp4
```

## 46.17 Picture-in-picture (overlay)

```bash
# Small video overlaid on large video (bottom-right corner)
ffmpeg -i main.mp4 -i webcam.mp4 \
    -filter_complex "[1:v]scale=320:240[pip];[0:v][pip]overlay=W-w-20:H-h-20" \
    -c:a copy output.mp4
```

## 46.18 Side-by-side

```bash
# Two videos side by side
ffmpeg -i left.mp4 -i right.mp4 \
    -filter_complex "[0:v]scale=640:480[l];[1:v]scale=640:480[r];[l][r]hstack=inputs=2" \
    -c:a copy sidebyside.mp4

# Vertical stack (top/bottom)
ffmpeg -i top.mp4 -i bottom.mp4 \
    -filter_complex "[0:v]scale=1280:360[t];[1:v]scale=1280:360[b];[t][b]vstack=inputs=2" \
    output.mp4
```

## 46.19 Add subtitles

```bash
# Burn subtitles into video (hardcoded — can't be turned off)
ffmpeg -i input.mp4 -vf "subtitles=subs.srt" output.mp4

# Embed subtitles as a separate stream (soft subs — toggleable)
ffmpeg -i input.mp4 -i subs.srt -c copy -c:s mov_text output.mp4
```

---

## PART 6: Streaming & Automation

## 46.20 HLS (HTTP Live Streaming) — for web video players

```bash
# Convert to HLS (adaptive bitrate streaming)
ffmpeg -i input.mp4 \
    -c:v libx264 -crf 23 -preset fast \
    -c:a aac -b:a 128k \
    -hls_time 10 \          # 10-second segments
    -hls_list_size 0 \      # keep all segments in playlist
    -hls_segment_filename "segment_%03d.ts" \
    -f hls playlist.m3u8

# Multiple quality levels (adaptive)
ffmpeg -i input.mp4 \
    -filter_complex "[0:v]split=3[v1][v2][v3]" \
    -map "[v1]" -c:v:0 libx264 -b:v:0 5M -s:v:0 1920x1080 \
    -map "[v2]" -c:v:1 libx264 -b:v:1 2M -s:v:1 1280x720 \
    -map "[v3]" -c:v:2 libx264 -b:v:2 500k -s:v:2 640x360 \
    -map 0:a -c:a aac -b:a 128k \
    -f hls -hls_time 10 -master_pl_name master.m3u8 \
    -var_stream_map "v:0,a:0 v:1,a:0 v:2,a:0" \
    stream_%v/output.m3u8
```

## 46.21 Batch processing (shell script)

```bash
#!/bin/bash
# Convert all .avi files in a directory to .mp4

for file in *.avi; do
    output="${file%.avi}.mp4"
    echo "Converting: $file → $output"
    ffmpeg -i "$file" -c:v libx264 -crf 23 -preset fast -c:a aac "$output"
done
```

```bash
# Batch resize all images in a folder to 800px width
for img in *.jpg; do
    ffmpeg -i "$img" -vf "scale=800:-1" "resized_$img"
done
```

## 46.22 Node.js integration (fluent-ffmpeg)

```javascript
const ffmpeg = require("fluent-ffmpeg");

// Convert video
ffmpeg("input.mp4")
  .videoCodec("libx264")
  .audioCodec("aac")
  .size("1280x720")
  .output("output.mp4")
  .on("progress", (progress) => {
    console.log(`Processing: ${progress.percent?.toFixed(1)}%`);
  })
  .on("end", () => console.log("Done!"))
  .on("error", (err) => console.error("Error:", err))
  .run();

// Extract thumbnail
ffmpeg("input.mp4")
  .screenshots({
    timestamps: ["10%", "50%", "90%"],
    filename: "thumb_%i.png",
    folder: "./thumbnails",
    size: "320x240",
  });

// Get video info
ffmpeg.ffprobe("input.mp4", (err, metadata) => {
  console.log("Duration:", metadata.format.duration);
  console.log("Resolution:", metadata.streams[0].width, "×", metadata.streams[0].height);
});
```

## 46.23 Hardware acceleration (GPU encoding)

```bash
# NVIDIA GPU (NVENC) — 5-10× faster encoding
ffmpeg -i input.mp4 -c:v h264_nvenc -preset p4 -crf 23 -c:a aac output.mp4

# macOS (VideoToolbox)
ffmpeg -i input.mp4 -c:v h264_videotoolbox -b:v 5M -c:a aac output.mp4

# Intel Quick Sync (QSV)
ffmpeg -i input.mp4 -c:v h264_qsv -global_quality 23 -c:a aac output.mp4

# AMD (AMF)
ffmpeg -i input.mp4 -c:v h264_amf -quality balanced -c:a aac output.mp4

# Check available encoders
ffmpeg -encoders | grep -i nvenc
ffmpeg -encoders | grep -i videotoolbox
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Convert format | `ffmpeg -i in.avi out.mp4` |
| Trim (no reencode) | `ffmpeg -i in.mp4 -ss 00:01:00 -to 00:02:00 -c copy out.mp4` |
| Resize to 720p | `ffmpeg -i in.mp4 -vf "scale=-1:720" out.mp4` |
| Extract audio | `ffmpeg -i in.mp4 -vn -c:a copy out.aac` |
| Remove audio | `ffmpeg -i in.mp4 -an out.mp4` |
| Screenshot | `ffmpeg -i in.mp4 -ss 10 -frames:v 1 thumb.jpg` |
| GIF | `ffmpeg -i in.mp4 -vf "fps=10,scale=480:-1" out.gif` |
| Concat | `ffmpeg -f concat -i list.txt -c copy out.mp4` |
| Speed 2× | `ffmpeg -i in.mp4 -vf "setpts=0.5*PTS" -af "atempo=2" out.mp4` |
| Add text | `ffmpeg -i in.mp4 -vf "drawtext=text='Hi':fontsize=48:x=50:y=50" out.mp4` |
| HLS stream | `ffmpeg -i in.mp4 -f hls -hls_time 10 out.m3u8` |
| Normalize audio | `ffmpeg -i in.mp4 -af "loudnorm" out.mp4` |

---

## Summary

✅ Core concepts: container (MP4/MKV) vs codec (H.264/AAC) vs stream (video/audio/subtitle)
✅ Essential operations: convert, trim, resize, extract audio, screenshots
✅ Encoding: CRF quality control, presets (speed vs compression), H.264/H.265/AV1 comparison
✅ Filters: crop, rotate, speed, text overlay, fade, blur, denoise, normalize audio
✅ Complex operations: concat, picture-in-picture, side-by-side, subtitles
✅ Streaming: HLS with adaptive bitrate (multiple quality levels)
✅ Automation: batch scripts, Node.js integration (fluent-ffmpeg)
✅ GPU acceleration: NVENC, VideoToolbox, QSV (5-10× faster encoding)

## Key takeaways

**`-c copy` is your best friend.** When you just need to cut, trim, or remux (change container without changing content), use `-c copy`. It's instant, lossless, and doesn't re-encode.

**CRF controls quality, not file size.** CRF 18 = visually lossless, CRF 23 = good default, CRF 28 = smaller but lower quality. The file size varies based on content complexity — that's fine. Don't use `-b:v` (target bitrate) unless you need exact file size.

**Preset = time vs compression.** `slow` produces a 20% smaller file than `fast` at the same quality — but takes 4× longer to encode. For one-time archive: use `slow`. For real-time/batch: use `fast` or `veryfast`.

**H.264 for compatibility, AV1 for efficiency.** H.264 plays everywhere. AV1 is 50-70% smaller but encoding is slow and playback requires modern hardware/browsers. Use H.264 for general distribution, AV1 for streaming at scale (YouTube, Netflix approach).

---

→ [Back to Chapter 45: LangChain & LangGraph](./45-LANGCHAIN-LANGGRAPH.md)
