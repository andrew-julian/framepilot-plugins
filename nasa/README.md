# NASA Space & Earth — FramePilot Plugin

A FramePilot source plugin that pulls stunning imagery from NASA's public APIs.
Each rotation, it picks randomly from your selected collections and delivers a full-resolution image to your Samsung Frame TV.

---

## Collections

| ID | Name | What you get |
|----|------|-------------|
| `apod` | Astronomy Picture of the Day | One hand-picked space image per day, curated by NASA astronomers since 1995. |
| `epic` | Earth from Space (EPIC) | Full-disk Earth photos taken by the DSCOVR satellite from 1.5M km away. |
| `mars_curiosity` | Mars — Curiosity Rover | Raw images from the Curiosity rover's cameras on the Martian surface. |
| `mars_perseverance` | Mars — Perseverance Rover | Raw images from the Perseverance rover and its Ingenuity helicopter. |
| `jwst` | James Webb Space Telescope | Infrared images from JWST, sourced via the NASA Image Library. |
| `image_library` | NASA Image Library | Keyword search across NASA's full archive of photography and imagery. |

---

## Installation

### 1. Copy the plugin

```bash
cp -r /path/to/nasa ~/Library/Application\ Support/FramePilot/plugins/nasa
```

Or manually: open Finder, press `⌘⇧G`, paste `~/Library/Application Support/FramePilot/plugins/`, and drop this folder in.

### 2. Install dependencies

```bash
cd ~/Library/Application\ Support/FramePilot/plugins/nasa
bash setup.sh
```

This installs [Pillow](https://pillow.readthedocs.io/) (for image conversion) via pip.

### 3. Enable in FramePilot

Open FramePilot → **Sources** → find **NASA Space & Earth** → toggle it on.

---

## Configuration

Configure via the **Sources** tab in FramePilot — click the source card to expand settings.

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| NASA API Key | text | *(blank)* | Free key from [api.nasa.gov](https://api.nasa.gov/). Leave blank to use `DEMO_KEY` (~30 req/hr). |
| Collections | checkbox group | APOD + JWST | Which sources to draw from. FramePilot picks randomly each rotation. |
| Image Library keyword | text | `nebula` | Search term for NASA Image Library and JWST queries. |
| Prefer HD | toggle | on | Download highest-resolution version when available. |
| Max APOD age (days) | slider | 365 | For APOD only: restricts picks to images within this many days. 0 = no limit. |

### Getting a NASA API key

1. Visit [api.nasa.gov](https://api.nasa.gov/)
2. Fill in the simple form — no credit card needed
3. Your key is emailed instantly
4. Paste it into the NASA API Key field in FramePilot

The `DEMO_KEY` works without registration but is rate-limited to ~30 requests per hour per IP. For a household using FramePilot all day, a personal key is recommended.

---

## Requirements

- macOS (this plugin is currently macOS-only)
- Python 3.8+
- Pillow 10+

---

## Build your own plugin

This plugin is the official reference example for the FramePilot plugin SDK.

👉 [framepilot.app/docs/custom-source](https://framepilot.app/docs/custom-source)

---

## License

MIT — use freely, fork, modify, share.
