# framepilot-plugins

Official source plugins for [FramePilot](https://framepilot.app) — the Samsung Frame TV art rotation app.

Each subdirectory is a self-contained, installable plugin. Drop any of them into FramePilot's plugins folder and they appear instantly in the Sources tab.

---

## Available plugins

| Plugin | Description |
|--------|-------------|
| [nasa/](./nasa/) | NASA Space & Earth — APOD, Earth from space, Mars rovers, James Webb Telescope |

More coming soon.

---

## Installing a plugin

1. Copy the plugin directory to `~/Library/Application Support/FramePilot/plugins/<plugin-name>/`
2. Run `bash setup.sh` inside the plugin directory (if present) to install dependencies
3. Open FramePilot → **Sources** — the plugin appears automatically

---

## Build your own

The [NASA plugin](./nasa/) is the official reference example.

Full developer documentation: [framepilot.app/docs/custom-source](https://framepilot.app/docs/custom-source)

---

## License

MIT
