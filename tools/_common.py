"""Shared helpers for the research tools: polite HTTP with cache/backoff,
number formatting, and labelled contact sheets."""

import hashlib
import json
import os
import random
import re
import sys
import threading
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

USER_AGENT = "roblox-gamesmith-research/1.0 (game-design research; public endpoints only; low volume)"
CACHE_DIR = os.path.expanduser("~/.cache/roblox-gamesmith/research")

_rate_lock = threading.Lock()
_last_request = [0.0]
MIN_INTERVAL = 0.12  # seconds between requests across threads


class HttpError(Exception):
    def __init__(self, status, url, body=""):
        super().__init__(f"HTTP {status} for {url}: {body[:200]}")
        self.status = status
        self.url = url
        self.body = body


def _throttle():
    with _rate_lock:
        wait = _last_request[0] + MIN_INTERVAL - time.monotonic()
        if wait > 0:
            time.sleep(wait)
        _last_request[0] = time.monotonic()


def _cache_path(namespace, key):
    h = hashlib.sha1(key.encode()).hexdigest()
    return os.path.join(CACHE_DIR, namespace, h[:2], h + ".json")


def http_json(url, *, method="GET", body=None, ttl=600, namespace="http", retries=5, headers=None):
    """GET/POST returning parsed JSON. Cached on disk for `ttl` seconds (0 disables).
    Retries 429 and 5xx with exponential backoff, honouring Retry-After."""
    data = json.dumps(body).encode() if body is not None else None
    key = f"{method} {url} {data.decode() if data else ''}"
    path = _cache_path(namespace, key)
    if ttl and os.path.exists(path) and time.time() - os.path.getmtime(path) < ttl:
        try:
            with open(path) as f:
                return json.load(f)
        except (OSError, ValueError):
            pass
    hdrs = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    if data is not None:
        hdrs["Content-Type"] = "application/json"
    hdrs.update(headers or {})
    delay = 1.0
    for attempt in range(retries):
        _throttle()
        req = urllib.request.Request(url, data=data, method=method, headers=hdrs)
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                raw = r.read().decode("utf-8", "replace")
            result = json.loads(raw) if raw.strip() else {}
            if ttl:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                tmp = path + f".{os.getpid()}.tmp"
                with open(tmp, "w") as f:
                    f.write(raw)
                os.replace(tmp, path)
            return result
        except urllib.error.HTTPError as e:
            text = e.read().decode("utf-8", "replace") if e.fp else ""
            if (e.code == 429 or e.code >= 500) and attempt < retries - 1:
                ra = (e.headers.get("Retry-After") or e.headers.get("x-ratelimit-reset")) if e.headers else None
                try:
                    wait = float(ra) if ra else delay
                except ValueError:
                    wait = delay
                wait = min(max(wait, delay), 60) + random.uniform(0, 0.5)
                print(f"  [{e.code}] backing off {wait:.1f}s: {short_url(url)}", file=sys.stderr)
                time.sleep(wait)
                delay *= 2
                continue
            raise HttpError(e.code, url, text) from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt < retries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise HttpError(0, url, str(e)) from None
    raise HttpError(0, url, "retries exhausted")


def try_json(url, **kw):
    """http_json that returns None instead of raising on 4xx/network failure."""
    try:
        return http_json(url, **kw)
    except HttpError as e:
        if os.environ.get("RESEARCH_DEBUG"):
            print(f"  ! {e}", file=sys.stderr)
        return None


def download(url, dest, ttl=86400):
    """Download a binary file unless a fresh copy already exists."""
    if os.path.exists(dest) and os.path.getsize(dest) > 0 and time.time() - os.path.getmtime(dest) < ttl:
        return dest
    os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
    delay = 1.0
    for attempt in range(4):
        _throttle()
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(req, timeout=60) as r, open(dest + ".part", "wb") as f:
                while chunk := r.read(65536):
                    f.write(chunk)
            os.replace(dest + ".part", dest)
            return dest
        except urllib.error.HTTPError as e:
            if (e.code == 429 or e.code >= 500) and attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            raise HttpError(e.code, url) from None
        except (urllib.error.URLError, TimeoutError, ConnectionError) as e:
            if attempt < 3:
                time.sleep(delay)
                delay *= 2
                continue
            raise HttpError(0, url, str(e)) from None


def short_url(url):
    p = urllib.parse.urlsplit(url)
    return p.netloc + p.path


# ---------- formatting ----------

def fmt_num(n):
    if n is None:
        return "?"
    n = float(n)
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if abs(n) >= div:
            v = n / div
            return f"{v:.1f}{suf}" if v < 100 else f"{v:.0f}{suf}"
    return f"{n:.0f}"


def parse_time(s):
    if not s:
        return None
    s = s.replace("Z", "+00:00")
    s = re.sub(r"\.(\d{6})\d+", r".\1", s)  # trim >6 fractional digits
    try:
        dt = datetime.fromisoformat(s)
    except ValueError:
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def days_since(s):
    dt = parse_time(s) if isinstance(s, str) else s
    if not dt:
        return None
    return max((datetime.now(timezone.utc) - dt).total_seconds() / 86400, 0)


def fmt_age(days):
    if days is None:
        return "?"
    if days < 1:
        return f"{days * 24:.0f}h"
    if days < 60:
        return f"{days:.0f}d"
    if days < 730:
        return f"{days / 30.4:.0f}mo"
    return f"{days / 365.25:.1f}y"


def fmt_dur(sec):
    if sec is None:
        return "?"
    sec = int(sec)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m}:{s:02d}"


def slugify(text, maxlen=40):
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").lower()
    return text[:maxlen].strip("-") or "untitled"


def clip(text, n):
    text = text or ""
    return text if len(text) <= n else text[: n - 1] + "…"


def display_name(text):
    """Drop emoji/symbols and bracketed event tags noise for compact tables; keep letters."""
    t = "".join(ch for ch in (text or "") if unicodedata.category(ch)[0] in "LNPZ" or ch in "&+'-!?")
    t = re.sub(r"\[\s*\]|\(\s*\)", "", t)
    return re.sub(r"\s+", " ", t).strip() or (text or "").strip()


# ---------- contact sheet ----------

def _font(size, bold=False):
    from PIL import ImageFont
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for c in candidates:
        if os.path.exists(c):
            try:
                return ImageFont.truetype(c, size)
            except OSError:
                pass
    return ImageFont.load_default(size=size)


def _ascii_safe(text):
    # Fonts used here lack emoji glyphs; strip what would render as boxes.
    return "".join(ch for ch in text if ord(ch) < 0x2000 or unicodedata.category(ch)[0] in "LN").strip()


def contact_sheet(items, out_path, title="", subtitle="", cols=3, tile_w=480, tile_h=270):
    """items: list of (image_path, label). Each image is letterboxed into a tile_w x tile_h
    cell with its label underneath. Writes a JPEG and returns its path."""
    from PIL import Image, ImageDraw, ImageOps

    items = [(p, l) for p, l in items if p and os.path.exists(p)]
    if not items:
        return None
    cols = max(1, min(cols, len(items)))
    rows = (len(items) + cols - 1) // cols
    pad, label_h = 10, 30
    head_h = 64 if title else 0
    W = cols * tile_w + (cols + 1) * pad
    H = head_h + rows * (tile_h + label_h) + (rows + 1) * pad
    bg, cell_bg, fg, dim = (24, 24, 28), (12, 12, 14), (240, 240, 240), (170, 170, 178)
    sheet = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(sheet)
    f_title, f_sub, f_label = _font(26, bold=True), _font(16), _font(18, bold=True)
    if title:
        d.text((pad + 2, 10), clip(_ascii_safe(title), 90), font=f_title, fill=fg)
        if subtitle:
            d.text((pad + 2, 40), clip(_ascii_safe(subtitle), 150), font=f_sub, fill=dim)
    for i, (path, label) in enumerate(items):
        r, c = divmod(i, cols)
        x = pad + c * (tile_w + pad)
        y = head_h + pad + r * (tile_h + label_h + pad)
        d.rectangle([x, y, x + tile_w - 1, y + tile_h - 1], fill=cell_bg)
        try:
            im = Image.open(path)
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((tile_w, tile_h), Image.LANCZOS)
            sheet.paste(im, (x + (tile_w - im.width) // 2, y + (tile_h - im.height) // 2))
        except Exception as e:  # unreadable image: leave the cell empty but labelled
            d.text((x + 8, y + 8), f"unreadable: {e.__class__.__name__}", font=f_sub, fill=dim)
        d.text((x + 4, y + tile_h + 5), clip(_ascii_safe(label), 48), font=f_label, fill=fg)
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    sheet.save(out_path, "JPEG", quality=85, optimize=True)
    return out_path
