# Chapter 1 — Get the Data

[← Overview](chapter-00-overview.md) | [Next → Chapter 2: Chunk the Text](chapter-02-chunking.md)

---

## Goal

Download the Emacs manual from GNU and convert it to clean plaintext.

---

## Why the Emacs Manual?

It's freely available, well-structured, ~600 pages of dense technical writing — perfect for training a small domain-specific model. And we'll actually use the result.

---

## Download & Parse

```python
# src/get_data.py
import requests
from bs4 import BeautifulSoup
from pathlib import Path

def download_emacs_manual():
    """Download Emacs manual HTML and extract plaintext."""
    url = "https://www.gnu.org/software/emacs/manual/html_mono/emacs.html"
    resp = requests.get(url, timeout=60)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove navigation, headers, footers
    for tag in soup.find_all(["nav", "header", "footer", "script"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)

    Path("data").mkdir(exist_ok=True)
    Path("data/emacs-manual.txt").write_text(text, encoding="utf-8")
    print(f"Saved {len(text):,} characters to data/emacs-manual.txt")

if __name__ == "__main__":
    download_emacs_manual()
```

---

## Run It

```bash
python src/get_data.py
# Saved 1,247,832 characters to data/emacs-manual.txt
```

---

## Verify

```python
text = open("data/emacs-manual.txt").read()
print(text[:200])
# Should show clean Emacs manual text, no HTML tags
```

---

## What You Learned

- How to fetch and parse HTML with `requests` + `BeautifulSoup`
- The Emacs manual is our training corpus (~1.2M characters)
- Output: `data/emacs-manual.txt` — clean plaintext ready for chunking

---

[← Overview](chapter-00-overview.md) | [Next → Chapter 2: Chunk the Text](chapter-02-chunking.md)
