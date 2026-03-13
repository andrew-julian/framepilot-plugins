#!/usr/bin/env python3
"""
FramePilot plugin: NASA Space & Earth
Pulls images from NASA's public APIs and outputs a PNG to stdout.

Collections:
  apod              — Astronomy Picture of the Day
  epic              — Earth from Space (EPIC / DSCOVR satellite)
  mars_curiosity    — Mars, Curiosity Rover
  mars_perseverance — Mars, Perseverance Rover
  jwst              — James Webb Space Telescope (via Image Library)
  image_library     — NASA Image & Video Library (keyword search)

Environment variables set by FramePilot:
  FRAMEPILOT_CONFIG      — JSON string of user config
  FRAMEPILOT_PLUGIN_DIR  — path to this plugin directory
  FRAMEPILOT_CACHE_DIR   — per-plugin persistent cache directory
  FRAMEPILOT_ROTATION_ID — unique UUID for this rotation tick
"""

import os
import sys
import json
import io
import random
import time
import datetime
import hashlib
import urllib.request
import urllib.parse
import urllib.error

try:
    from PIL import Image
except ImportError:
    print("Pillow is not installed. Run setup.sh to install dependencies.", file=sys.stderr)
    sys.exit(1)

# ── Config ────────────────────────────────────────────────────────────────────

config       = json.loads(os.environ.get("FRAMEPILOT_CONFIG", "{}"))
API_KEY      = config.get("nasa_api_key") or "DEMO_KEY"
COLLECTIONS  = config.get("collections", ["apod", "jwst"])
QUERY        = config.get("image_library_query") or "nebula"
PREFER_HD    = config.get("prefer_hd", True)
MAX_AGE_DAYS = int(config.get("max_age_days", 365))

CACHE_DIR    = os.environ.get("FRAMEPILOT_CACHE_DIR", "/tmp/framepilot-nasa-cache")
os.makedirs(CACHE_DIR, exist_ok=True)

CACHE_TTL    = 86400       # 24 hours in seconds
REQUEST_TIMEOUT = 20       # seconds per HTTP request

# ── Logging ───────────────────────────────────────────────────────────────────

def log(msg):
    print(f"[nasa] {msg}", file=sys.stderr)

# ── Caching ───────────────────────────────────────────────────────────────────

def cache_path(key):
    safe = hashlib.md5(key.encode()).hexdigest()
    return os.path.join(CACHE_DIR, f"{safe}.cache")

def cache_get(key):
    """Return cached bytes if fresh, else None."""
    path = cache_path(key)
    if os.path.exists(path):
        age = time.time() - os.path.getmtime(path)
        if age < CACHE_TTL:
            try:
                with open(path, "rb") as f:
                    return f.read()
            except OSError:
                pass
    return None

def cache_put(key, data):
    """Write bytes to cache."""
    try:
        with open(cache_path(key), "wb") as f:
            f.write(data)
    except OSError as e:
        log(f"Cache write failed ({key}): {e}")

# ── HTTP ──────────────────────────────────────────────────────────────────────

def http_get(url):
    """Fetch URL, return bytes. Raises on HTTP error."""
    req = urllib.request.Request(url, headers={"User-Agent": "FramePilot/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=REQUEST_TIMEOUT) as resp:
            return resp.read()
    except urllib.error.HTTPError as e:
        raise ValueError(f"HTTP Error {e.code}: {e.reason} for {url}") from e

def http_get_json(url):
    return json.loads(http_get(url))

def download_image(url, cache_key=None):
    """Download image bytes, optionally caching by key."""
    if cache_key:
        cached = cache_get(cache_key)
        if cached:
            log(f"Cache hit: {cache_key}")
            return cached
    data = http_get(url)
    if cache_key:
        cache_put(cache_key, data)
    return data

# ── Image conversion ──────────────────────────────────────────────────────────

def to_png(raw_bytes):
    """Convert any image format to PNG bytes."""
    img = Image.open(io.BytesIO(raw_bytes)).convert("RGB")
    out = io.BytesIO()
    img.save(out, format="PNG", optimize=False)
    return out.getvalue()

# ── Collections ───────────────────────────────────────────────────────────────

def fetch_apod():
    """Astronomy Picture of the Day — random date within max_age window."""
    today = datetime.date.today()

    if MAX_AGE_DAYS > 0:
        max_back = min(MAX_AGE_DAYS, 9000)  # APOD started 1995-06-16
        days_back = random.randint(0, max_back)
        target_date = (today - datetime.timedelta(days=days_back)).isoformat()
        url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={target_date}&hd=True"
    else:
        # Pick a random image from the last 20 returned
        url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&count=20&hd=True"

    data = http_get_json(url)
    if isinstance(data, list):
        # Filter to image-only entries
        images = [d for d in data if d.get("media_type") == "image"]
        if not images:
            raise ValueError("No image entries in APOD batch")
        data = random.choice(images)

    if data.get("media_type") != "image":
        raise ValueError(f"APOD entry is not an image (media_type={data.get('media_type')})")

    img_url = data.get("hdurl" if PREFER_HD else "url") or data["url"]
    date_str = data.get("date", "unknown")
    log(f"APOD: {data.get('title', 'untitled')} ({date_str})")

    raw = download_image(img_url, cache_key=f"apod_{date_str}")
    return raw


def fetch_epic():
    """Earth Polychromatic Imaging Camera — latest natural colour images."""
    # Get the most recent available date
    dates_url = f"https://api.nasa.gov/EPIC/api/natural/all?api_key={API_KEY}"
    dates = http_get_json(dates_url)
    if not dates:
        raise ValueError("No EPIC dates available")

    # Pick from the 3 most recent dates for variety
    recent_dates = [d["date"] for d in dates[:3]]
    chosen_date = random.choice(recent_dates)
    date_slug = chosen_date.replace("-", "/")

    images_url = f"https://api.nasa.gov/EPIC/api/natural/date/{chosen_date}?api_key={API_KEY}"
    images = http_get_json(images_url)
    if not images:
        raise ValueError(f"No EPIC images for {chosen_date}")

    item = random.choice(images[:10])
    img_name = item["image"]
    img_url = (
        f"https://api.nasa.gov/EPIC/archive/natural/{date_slug}/png/{img_name}.png"
        f"?api_key={API_KEY}"
    )
    log(f"EPIC: {img_name} ({chosen_date})")
    raw = download_image(img_url, cache_key=f"epic_{img_name}")
    return raw


def fetch_mars(rover):
    """Mars Rover imagery via NASA Image Library.

    The api.nasa.gov/mars-photos endpoint was decommissioned (it was a
    third-party Heroku app). We use the NASA Image & Video Library instead,
    which has thousands of high-quality rover images.
    """
    rover_queries = {
        "curiosity":    "Curiosity rover Mars surface",
        "perseverance": "Perseverance rover Mars Jezero",
    }
    q = rover_queries.get(rover, f"{rover} rover Mars")
    encoded_q = urllib.parse.quote(q)
    search_url = (
        f"https://images-api.nasa.gov/search"
        f"?q={encoded_q}&media_type=image&page_size=20"
    )
    data = http_get_json(search_url)
    items = data.get("collection", {}).get("items", [])
    items = [it for it in items if it.get("href")]
    if not items:
        raise ValueError(f"No image library results for Mars {rover}")

    random.shuffle(items)
    for item in items[:5]:
        try:
            manifest = http_get_json(item["href"])
            jpegs = [u for u in manifest if u.lower().endswith("~orig.jpg")]
            if not jpegs:
                jpegs = [u for u in manifest if u.lower().endswith(".jpg")]
            if not jpegs:
                continue
            nasa_id = item.get("data", [{}])[0].get("nasa_id", jpegs[0].split("/")[-1])
            log(f"Mars {rover}: {nasa_id}")
            raw = download_image(jpegs[0], cache_key=f"mars_{rover}_{nasa_id}")
            return raw
        except Exception as e:
            log(f"Mars {rover} item failed: {e}")
            continue

    raise ValueError(f"All Mars {rover} image library results failed")


def fetch_image_library(search_query=None):
    """NASA Image & Video Library — keyword search, images only."""
    q = search_query or QUERY
    encoded_q = urllib.parse.quote(q)
    search_url = (
        f"https://images-api.nasa.gov/search"
        f"?q={encoded_q}&media_type=image&page_size=20"
    )
    data = http_get_json(search_url)
    items = data.get("collection", {}).get("items", [])

    # Filter to items that have an asset link
    items = [it for it in items if it.get("href")]
    if not items:
        raise ValueError(f"No image library results for '{q}'")

    # Shuffle and try up to 5 items (some may have no downloadable JPEG)
    random.shuffle(items)
    for item in items[:5]:
        try:
            asset_url = item["href"]
            manifest = http_get_json(asset_url)

            # Find the best JPEG in the manifest
            jpegs = [u for u in manifest if u.lower().endswith("~orig.jpg")]
            if not jpegs:
                jpegs = [u for u in manifest if u.lower().endswith(".jpg")]
            if not jpegs:
                continue

            img_url = jpegs[0]
            # Use NASA ID as cache key
            nasa_id = item.get("data", [{}])[0].get("nasa_id", img_url.split("/")[-1])
            log(f"Image Library: '{q}' → {nasa_id}")
            raw = download_image(img_url, cache_key=f"lib_{nasa_id}")
            return raw
        except Exception as e:
            log(f"Image library item failed: {e}")
            continue

    raise ValueError(f"All image library results for '{q}' failed")


def fetch_jwst():
    """James Webb Space Telescope — image library search."""
    # JWST images are in the NASA image library under various keywords.
    # Build a query combining the user keyword with JWST identifiers.
    q = f"James Webb {QUERY}"
    return fetch_image_library(search_query=q)


# ── Dispatch ──────────────────────────────────────────────────────────────────

FETCHERS = {
    "apod":              fetch_apod,
    "epic":              fetch_epic,
    "mars_curiosity":    lambda: fetch_mars("curiosity"),
    "mars_perseverance": lambda: fetch_mars("perseverance"),
    "jwst":              fetch_jwst,
    "image_library":     fetch_image_library,
}

available = [c for c in COLLECTIONS if c in FETCHERS]
if not available:
    log(f"No valid collections in config: {COLLECTIONS}")
    log(f"Valid options: {list(FETCHERS.keys())}")
    sys.exit(1)

# Shuffle so we don't always try in the same order
random.shuffle(available)
last_error = None

for collection in available:
    try:
        log(f"Trying collection: {collection}")
        raw = FETCHERS[collection]()
        png = to_png(raw)
        sys.stdout.buffer.write(png)
        log(f"Done — {len(png):,} bytes PNG")
        sys.exit(0)
    except Exception as e:
        log(f"[{collection}] failed: {e}")
        last_error = e
        continue

log(f"All collections failed. Last error: {last_error}")
sys.exit(1)
