# Chapter 58: QR Codes — How They Work (and How to Generate Them)

## What you'll learn

- How QR codes encode data (the structure behind those black and white squares)
- The anatomy: finder patterns, alignment, timing, data, error correction
- Encoding modes: numeric, alphanumeric, byte, kanji
- Error correction: how a damaged QR code still scans (Reed-Solomon)
- Generating QR codes programmatically (JavaScript, Python, Java)
- Real-world applications and creative uses

---

## PART 1: QR Code Anatomy

## 58.1 What is a QR code?

```
QR = "Quick Response" (invented 1994 by Denso Wave for Toyota car parts)

A 2D barcode that encodes data in a grid of black/white modules (squares).
Can store: URLs, text, phone numbers, WiFi credentials, vCards, any binary data.

Key advantages over 1D barcodes:
• Stores 100× more data (up to 7,089 numeric or 4,296 alphanumeric characters)
• Reads from any angle (360° rotation)
• Works when partially damaged (up to 30% destroyed and still scans)
• Fast to scan (designed for high-speed reading)
```

## 58.2 Structure of a QR code

```
┌─────────────────────────────────────────────────────┐
│ ■■■■■■■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ □ ■■■■■■■ │
│ ■□□□□□■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ □ ■□□□□□■ │
│ ■□■■■□■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ □ ■□■■■□■ │
│ ■□■■■□■ □ ┄┄┄ DATA REGION ┄┄┄┄┄ □ ■□■■■□■ │
│ ■□■■■□■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ □ ■□■■■□■ │
│ ■□□□□□■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ □ ■□□□□□■ │
│ ■■■■■■■ □■□■□■□■□■□■□■□■□■□■□■□ □ ■■■■■■■ │
│ □□□□□□□ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ □ □□□□□□□ │
│ ┄┄┄┄┄┄┄ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ ┄┄┄┄┄┄┄ │
│ ┄┄┄┄┄┄┄┄┄┄┄┄ DATA + ERROR ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │
│ ┄┄┄┄┄┄┄┄┄┄┄┄ CORRECTION  ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │
│ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │
│ □□□□□□□ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │
│ ■■■■■■■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ ■■■■■ ┄┄┄┄┄┄┄┄ │
│ ■□□□□□■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ ■□□□■ ┄┄┄┄┄┄┄┄ │
│ ■□■■■□■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ ■□■□■ ┄┄┄┄┄┄┄┄ │
│ ■□■■■□■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ ■□□□■ ┄┄┄┄┄┄┄┄ │
│ ■□■■■□■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ ■■■■■ ┄┄┄┄┄┄┄┄ │
│ ■□□□□□■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │
│ ■■■■■■■ □ ┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄ │
└─────────────────────────────────────────────────────┘

 FINDER        TIMING    ALIGNMENT    DATA + EC
 PATTERNS      PATTERN   PATTERN      MODULES
```

## 58.3 Components explained

| Component | Location | Purpose |
|-----------|----------|---------|
| **Finder patterns** (3) | Top-left, top-right, bottom-left corners | Allow scanner to detect the QR code and determine orientation — scans from ANY angle |
| **Alignment pattern** | Near bottom-right (larger QR codes have multiple) | Corrects for distortion (curved surfaces, angled scanning) |
| **Timing patterns** | Horizontal + vertical lines between finders | Help scanner determine module (cell) positions and size |
| **Format information** | Near finder patterns | Error correction level + mask pattern (tells scanner how to decode) |
| **Version information** | For Version 7+ (larger codes) | QR code version (determines size: Version 1=21×21, Version 40=177×177) |
| **Data + EC modules** | Everything else | Your actual data + error correction bytes |
| **Quiet zone** | 4-module white border around the QR | Separation from surroundings (essential — without it, scanners can't find the edge) |

## 58.4 Why finder patterns look like that

```
■■■■■■■
■□□□□□■     Ratio of black:white:black:white:black = 1:1:3:1:1
■□■■■□■     
■□■■■□■     This specific ratio is unique — doesn't occur naturally.
■□■■■□■     A scanner scans in straight lines. When it finds 1:1:3:1:1
■□□□□□■     in ANY direction, it knows: "this is a QR code corner."
■■■■■■■     
                Three corners → determine exact position + rotation.
```

---

## PART 2: How Data is Encoded

## 58.5 Encoding modes

| Mode | Characters | Bits per char | Use case |
|------|-----------|--------------|----------|
| **Numeric** | 0-9 | 3.33 (10 bits per 3 digits) | Phone numbers, IDs |
| **Alphanumeric** | 0-9, A-Z, space, $%*+-./:  | 5.5 (11 bits per 2 chars) | Short text, URLs (uppercase) |
| **Byte** | Any (UTF-8, binary) | 8 bits per byte | URLs, general text, binary data |
| **Kanji** | Japanese characters | 13 bits per char | Japanese text |

The encoder picks the most efficient mode (or mixes modes within one QR code):
```
"1234567890"        → Numeric mode (most compact)
"HELLO WORLD"       → Alphanumeric mode
"https://example.com" → Byte mode (lowercase = can't use alphanumeric)
```

## 58.6 Encoding process (step by step)

```
Input: "HELLO"

Step 1: Choose mode → Alphanumeric (all uppercase)
Step 2: Mode indicator → 0010 (4 bits: alphanumeric = 0010)
Step 3: Character count → 000000101 (length=5 in 9 bits for Version 1)
Step 4: Encode data:
        H=17, E=14 → pair (17×45 + 14) = 779 → 01100001011 (11 bits)
        L=21, L=21 → pair (21×45 + 21) = 966 → 01111000110 (11 bits)
        O=24       → single: 24 → 011000 (6 bits, since odd character)
Step 5: Terminator → 0000 (end marker)
Step 6: Pad to fill capacity → alternating 11101100 00010001

Result (data bits): 0010 000000101 01100001011 01111000110 011000 0000 ...

Step 7: Error correction → compute Reed-Solomon codes → append
Step 8: Place in grid → zigzag pattern filling modules
Step 9: Apply mask → XOR with mask pattern (improves scannability)
Step 10: Add format/version info
```

## 58.7 QR code versions (sizes)

| Version | Size | Max data (bytes, EC level L) |
|---------|------|------------------------------|
| 1 | 21×21 | 17 |
| 2 | 25×25 | 32 |
| 5 | 37×37 | 106 |
| 10 | 57×57 | 271 |
| 20 | 97×97 | 858 |
| 40 | 177×177 | 2,953 |

Each version adds 4 modules per side. The encoder picks the smallest version that fits your data.

---

## PART 3: Error Correction

## 58.8 Reed-Solomon error correction

```
QR codes can be read even when DAMAGED (dirty, torn, obscured):

EC Level | Redundancy | Data recoverable if damaged
─────────────────────────────────────────────────────
  L      |    7%      | Low protection (smallest QR code)
  M      |   15%      | Medium (default — good balance)
  Q      |   25%      | Quartile (good for printing)
  H      |   30%      | High (works with logo in center!)

HOW IT WORKS (simplified):
1. Your data: [D1, D2, D3, D4, D5]
2. Reed-Solomon math generates EXTRA bytes: [EC1, EC2, EC3, EC4]
3. Stored in QR: [D1, D2, D3, D4, D5, EC1, EC2, EC3, EC4]
4. If D3 is damaged (unreadable), the EC bytes contain enough
   information to RECONSTRUCT D3.

It's the same math used in:
• CDs (scratches don't skip songs)
• DVDs / Blu-ray
• Deep space communication (Voyager, Mars rovers)
• RAID storage arrays
```

## 58.9 Why you can put logos in QR codes

```
With EC Level H (30% error correction):
• The scanner treats the logo as "damage"
• As long as the logo covers < 30% of the data area, the code still scans
• That's why you see QR codes with company logos in the center

RULES for logo placement:
• Center of the code (furthest from finder patterns)
• Cover no more than ~25% of the total area (leave margin)
• Use EC Level H
• Test it! Some logos break specific modules that matter more

┌─────────────────────────┐
│ ■■■■■  ┄┄┄┄┄┄  ■■■■■  │
│ ■□□□■  ┄┄┄┄┄┄  ■□□□■  │
│ ■□■□■  ┄┄┄┄┄┄  ■□■□■  │
│ ┄┄┄┄┄  ┌────┐  ┄┄┄┄┄  │
│ ┄┄┄┄┄  │LOGO│  ┄┄┄┄┄  │  ← logo in center = "damage" EC corrects
│ ┄┄┄┄┄  └────┘  ┄┄┄┄┄  │
│ ■■■■■  ┄┄┄┄┄┄  ┄┄┄┄┄  │
│ ■□□□■  ┄┄┄┄┄┄  ┄┄┄┄┄  │
│ ■□■□■  ┄┄┄┄┄┄  ┄┄┄┄┄  │
└─────────────────────────┘
```

---

## PART 4: Masking (Why QR Codes Look "Random")

## 58.10 The masking step

After placing data modules, the QR code might have large areas of solid black or white, which confuse scanners. **Masking** XORs the data with a pattern to break up these areas.

```
8 mask patterns are tried. The one that produces the most "balanced"
result (fewest large same-colour areas) is used.

Mask 0: (row + col) % 2 == 0       (checkerboard)
Mask 1: row % 2 == 0                (horizontal stripes)
Mask 2: col % 3 == 0                (vertical stripes)
Mask 3: (row + col) % 3 == 0
Mask 4: (row/2 + col/3) % 2 == 0
Mask 5: (row*col)%2 + (row*col)%3 == 0
Mask 6: ((row*col)%2 + (row*col)%3) % 2 == 0
Mask 7: ((row+col)%2 + (row*col)%3) % 2 == 0

The chosen mask number is stored in the format information (near finder patterns).
Scanner reads the mask number → XORs data to reverse → reads original data.
```

---

## PART 5: Generate QR Codes Programmatically

## 58.11 JavaScript (browser + Node.js)

```bash
npm install qrcode
```

```javascript
// Node.js — generate to file
const QRCode = require("qrcode");

// Generate PNG file
await QRCode.toFile("./qr-output.png", "https://example.com", {
  errorCorrectionLevel: "H",
  width: 400,
  margin: 2,
  color: {
    dark: "#1e293b",   // dark modules colour
    light: "#ffffff",  // light modules colour
  },
});

// Generate data URL (for embedding in HTML)
const dataUrl = await QRCode.toDataURL("https://example.com", {
  errorCorrectionLevel: "M",
  width: 300,
});
// "data:image/png;base64,iVBORw0KGgo..."

// Generate SVG string
const svg = await QRCode.toString("https://example.com", { type: "svg" });

// Generate to canvas (browser)
const canvas = document.getElementById("qr-canvas");
QRCode.toCanvas(canvas, "https://example.com", { width: 256 });
```

**React component:**
```tsx
"use client";
import { useEffect, useRef } from "react";
import QRCode from "qrcode";

export function QRCodeComponent({ value, size = 200 }: { value: string; size?: number }) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (canvasRef.current) {
      QRCode.toCanvas(canvasRef.current, value, {
        width: size,
        margin: 2,
        errorCorrectionLevel: "M",
        color: { dark: "#0f172a", light: "#ffffff" },
      });
    }
  }, [value, size]);

  return <canvas ref={canvasRef} />;
}
```

## 58.12 Python

```bash
pip install qrcode[pil]
```

```python
import qrcode
from qrcode.constants import ERROR_CORRECT_H

# Simple generation
img = qrcode.make("https://example.com")
img.save("qr-simple.png")

# Advanced options
qr = qrcode.QRCode(
    version=None,  # auto-detect smallest version
    error_correction=ERROR_CORRECT_H,  # 30% error correction (supports logo)
    box_size=10,   # pixels per module
    border=4,      # quiet zone width (modules)
)
qr.add_data("https://example.com/my-page?ref=qr")
qr.make(fit=True)

img = qr.make_image(fill_color="#1e293b", back_color="white")
img.save("qr-custom.png")

# Generate SVG
import qrcode.image.svg
factory = qrcode.image.svg.SvgPathImage
img = qr.make_image(image_factory=factory)
img.save("qr-code.svg")

# QR code with logo overlay
from PIL import Image

qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
logo = Image.open("logo.png")

# Resize logo to fit in center (max 25% of QR area)
qr_size = qr_img.size[0]
logo_max = int(qr_size * 0.25)
logo = logo.resize((logo_max, logo_max))

# Paste logo in center
pos = ((qr_size - logo_max) // 2, (qr_size - logo_max) // 2)
qr_img.paste(logo, pos)
qr_img.save("qr-with-logo.png")
```

## 58.13 Java (ZXing library)

```java
// build.gradle.kts
// implementation("com.google.zxing:core:3.5.3")
// implementation("com.google.zxing:javase:3.5.3")

import com.google.zxing.*;
import com.google.zxing.client.j2se.MatrixToImageWriter;
import com.google.zxing.common.BitMatrix;
import com.google.zxing.qrcode.QRCodeWriter;
import com.google.zxing.qrcode.decoder.ErrorCorrectionLevel;

import java.nio.file.Path;
import java.util.Map;

public class QRGenerator {
    public static void generate(String text, String filePath, int size) throws Exception {
        QRCodeWriter writer = new QRCodeWriter();

        Map<EncodeHintType, Object> hints = Map.of(
            EncodeHintType.ERROR_CORRECTION, ErrorCorrectionLevel.H,
            EncodeHintType.MARGIN, 2,
            EncodeHintType.CHARACTER_SET, "UTF-8"
        );

        BitMatrix matrix = writer.encode(text, BarcodeFormat.QR_CODE, size, size, hints);
        MatrixToImageWriter.writeToPath(matrix, "PNG", Path.of(filePath));
    }

    public static void main(String[] args) throws Exception {
        generate("https://example.com", "qr-code.png", 400);
        System.out.println("QR code generated!");
    }
}
```

## 58.14 Reading/Decoding QR codes

```javascript
// Browser: use camera to scan
// npm install jsqr (for processing image data)
import jsQR from "jsqr";

// From a video frame (camera):
const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
const code = jsQR(imageData.data, canvas.width, canvas.height);
if (code) {
  console.log("Decoded:", code.data); // "https://example.com"
}
```

```python
# Python: decode from image
from pyzbar.pyzbar import decode
from PIL import Image

img = Image.open("qr-code.png")
results = decode(img)
for result in results:
    print(result.data.decode("utf-8"))  # "https://example.com"
```

---

## PART 6: Real-World Applications

## 58.15 What you can encode

| Use case | Data format | Example |
|----------|-------------|---------|
| **URL** | Plain text | `https://example.com` |
| **WiFi** | Special format | `WIFI:T:WPA;S:NetworkName;P:Password123;;` |
| **vCard** | Contact info | `BEGIN:VCARD\nVERSION:3.0\nFN:John Doe\nTEL:+123456\nEND:VCARD` |
| **Email** | mailto | `mailto:hi@example.com?subject=Hello` |
| **Phone** | tel | `tel:+1234567890` |
| **SMS** | sms | `sms:+1234567890?body=Hello` |
| **Location** | geo | `geo:51.5074,-0.1278` |
| **Calendar event** | vEvent | `BEGIN:VEVENT\nSUMMARY:Meeting\nDTSTART:20240801T100000\nEND:VEVENT` |
| **Plain text** | Any text | Up to ~4000 characters |
| **Binary** | Any bytes | Images, files, encrypted data |

## 58.16 WiFi QR code generator

```python
def wifi_qr(ssid, password, security="WPA", hidden=False):
    """Generate a QR code that auto-connects to WiFi when scanned."""
    hidden_str = "H:true;" if hidden else ""
    data = f"WIFI:T:{security};S:{ssid};P:{password};{hidden_str};"

    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    img.save(f"wifi-{ssid}.png")
    print(f"Scan to connect to '{ssid}'")

wifi_qr("MyHomeWiFi", "SuperSecret123")
```

**Print this and stick it on your fridge.** Guests scan → auto-connected. No typing passwords.

---

## Summary

✅ QR anatomy: finder patterns (orientation), timing (grid), alignment (distortion), data (content), quiet zone (border)
✅ Finder pattern magic: 1:1:3:1:1 ratio detected in any scan direction
✅ Encoding modes: numeric (3.3 bits/char), alphanumeric (5.5), byte (8), auto-selected
✅ Encoding process: mode indicator → count → data bits → padding → error correction → placement → masking
✅ Error correction: Reed-Solomon at 4 levels (L/M/Q/H), up to 30% damage tolerance
✅ Masking: 8 patterns tested, best one chosen to avoid large same-colour areas
✅ Logo in center: works because EC treats it as "damage" and corrects around it (use Level H)
✅ Generate: JavaScript (qrcode), Python (qrcode + PIL), Java (ZXing)
✅ Decode: jsQR (browser), pyzbar (Python)
✅ Applications: URLs, WiFi, contacts (vCard), email, phone, location, calendar events

## Key takeaways

**QR codes are brilliantly engineered.** Finder patterns (detected from any angle), error correction (works when 30% destroyed), masking (optimized for scanner readability), and encoding modes (compact representation for different data types) — all working together in a tiny square.

**Error correction is what makes QR codes practical.** Without it, a single smudge would make the code unreadable. With Level H, you can literally put a logo over 25% of the code and it still works. This is why QR codes survived the real world (dirt, damage, printing errors).

**Generating QR codes is trivial — understanding them is the value.** Any library generates one in 3 lines of code. But knowing HOW they work lets you make better decisions: choosing EC level, sizing, testing with logos, understanding why a code isn't scanning.

---

→ [Back to Chapter 57: SDKMAN](./57-SDKMAN-JAVA.md)
