# ⚡ IDLR — Internet Downloader

**Your personal, self‑hosted media download hub.**
Paste any link, and IDLR grabs the video or audio you want — no ads, no redirects, no third‑party uploads.
Everything runs locally on your machine.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![yt‑dlp](https://img.shields.io/badge/yt--dlp-latest-orange)
![spotdl](https://img.shields.io/badge/spotdl-latest-brightgreen)

> **Current version: v1.1.0** — see [Changelog](#-changelog) for what just got fixed.

---

## ✨ Features

- 🌐 **1000+ supported sites** via `yt‑dlp` – YouTube, TikTok, Instagram, Twitch, HLS / movie streams, and more
- 🎵 **Spotify audio** – tracks, albums & playlists via `spotdl` (format + bitrate respected)
- 🔍 **Live URL detection** – paste a link and the UI instantly recognises the platform (+ optional auto‑set of Mode/Format)
- 🖼️ **Thumbnail preview** – see title, uploader, duration & cover before you download
- 🎛️ **Settings toggles that actually work** – every switch changes real behaviour (see table below)
- ℹ️ **Premium Info panel (ⓘ)** – live app / yt‑dlp / FFmpeg versions, network URL, save folder, supported sites
- 📋 **Bulk history management** – search, select, rename ✏️, re‑download, or delete entries
- 🖥️ **Honest terminal output** – `python app.py` shows setup, per‑download progress, `DONE` / `FAILED` reasons
- 🔒 **100% private** – accounts, history & settings live in `~/.idlr_app/` on your PC only

---

## 🧩 Supported Platforms

| Platform | Video | Audio | Notes |
|----------|:-----:|:-----:|-------|
| YouTube  | ✅    | ✅    | Playlists supported |
| Spotify  | —     | ✅    | Via `spotdl`, MP3/M4A/OPUS/FLAC |
| SoundCloud | —  | ✅    | Auto‑switches to Audio |
| TikTok   | ✅    | ✅    |  |
| Twitter/X| ✅    | ✅    |  |
| Instagram| ✅    | ✅    |  |
| Twitch   | ✅    | ✅    | Clips & VODs |
| Vimeo    | ✅    | ✅    |  |
| Facebook | ✅    | ✅    |  |
| Reddit   | ✅    | ✅    |  |
| Dailymotion | ✅ | ✅    |  |
| HLS / `.m3u8` streams | ✅ | ✅ | Merged via FFmpeg |
| Direct `.mp4/.mkv/.webm` files | ✅ | ✅ | Downloaded directly |
| + 1000 more via `yt‑dlp` | ✅ | ✅ | Generic extractor fallback |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or newer
- `ffmpeg` recommended (required for MP3 extraction, video merging & thumbnails).
  The app ships `static-ffmpeg` as a fallback, but a system FFmpeg is more reliable.

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/idlr.git
cd idlr

# 2. Create a virtual environment (recommended)
python -m venv venv

# macOS / Linux
source venv/bin/activate

# Windows
venv\Scripts\activate

# 3. Install dependencies (app.py also auto-installs these on first run)
pip install flask yt-dlp static-ffmpeg spotdl

# 4. Install ffmpeg (if not already present)
# macOS:
brew install ffmpeg
# Ubuntu/Debian:
sudo apt install ffmpeg
# Windows:
winget install ffmpeg
```

### Run

```bash
python app.py
```

Then open **http://localhost:5000** (the browser opens automatically).
To use from your phone on the same Wi‑Fi, use the **Network URL** shown in the terminal or Settings.

---

## 🖥️ Usage

1. **Paste a URL** into the main input – the platform badge appears automatically.
2. **Select Mode / Quality / Format** from the dropdowns (or let Auto‑detect set them).
3. **Click “Download Now”** – watch live progress in the app *and* in the terminal.
4. **Track everything in History** – search, rename ✏️, re‑download ↺, or delete 🗑 entries.
5. **Customise via Settings** (gear icon) – every toggle takes effect immediately.
6. **Need help?** Click the **ⓘ Info button** for versions, system status & supported sites.

---

## ⚙️ Configuration

All settings live in the in‑app Settings panel (gear icon). They save to your browser instantly.

| Setting | Default | What it actually does |
|---------|---------|----------------------|
| Auto‑detect URL | ON | Auto‑switches Mode/Format on paste (e.g. Spotify → Audio/MP3). OFF = badge only, your options stay untouched |
| Download Thumbnail | ON | Embeds & saves cover art. OFF = no `writethumbnail`/`EmbedThumbnail`, faster + fewer FFmpeg failures |
| Full Playlist | OFF | ON = downloads the whole playlist even in single Video/Audio mode (`noplaylist=false`) |
| Hero Animations | ON | Animated hero title + chips. OFF = static, instant (adds `no-anim` to page) |
| Console Log | ON | Live download output under the progress bar. OFF = console hidden (`hide-console`) |
| Save Login Session | ON | Keeps you signed in across restarts (`localStorage`). OFF = session cleared on login |
| Save folder | `~/Downloads` | Where finished files go. Click the path bar to change |
| Update yt‑dlp + spotdl | — | One‑click updater in Settings (shows Updating… → Updated ✓ / error) |

> All data (accounts, history) is stored locally in `~/.idlr_app/` (`accounts.json`, `history.json`).
> Nothing is ever sent anywhere except the download request to the source site.

---

## 🗂️ Project Structure

```text
idlr/
├── app.py        # Flask backend (API, downloads, auth, history)
├── index.html    # Full frontend (single file: HTML + CSS + JS)
├── favicon.svg   # App icon
└── README.md     # This file
```

No `requirements.txt`, `static/` or `templates/` folders — the app is intentionally just these files.
`app.py` auto‑installs `flask`, `yt-dlp`, `static-ffmpeg`, `spotdl` on first run.

### Key API endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/api/register` · `/api/login` · `/api/google-login` | Auth |
| POST | `/api/profile` · `/api/prefs` | Profile + download prefs |
| POST | `/api/delete-account` | Permanently delete account + history |
| POST | `/api/download` | Start a download (`thumb`, `playlist_all` respected) |
| GET  | `/api/progress/<job_id>` (SSE) | Live progress stream |
| POST | `/api/preview` | Title / thumbnail / duration lookup |
| GET  | `/api/history` · DELETE `/api/history/clear` · DELETE `/api/history/remove` | History |
| POST | `/api/history/rename` | Rename a history entry ✏️ |
| GET  | `/api/info` | Versions (`version`, `ytdlp`, `ffmpeg`), network URL |
| POST | `/api/update-ytdlp` | Upgrade yt‑dlp + spotdl |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ffmpeg not found` / merge fails | Install FFmpeg and restart the terminal. Or turn **Download Thumbnail OFF** for aqueicker, less fragile download |
| YouTube `403` / `Sign in to confirm` | Settings → **Update yt‑dlp + spotdl**, then retry. Age‑restricted / DRM content cannot be downloaded |
| Spotify download fails | Make sure the link is public. Check bitrate/format choice. Terminal shows the exact `spotdl` reason |
| `No downloadable video found` | The page has no direct media (login wall, JS‑only player, or DRM like Netflix) |
| Save folder not writable | Pick an existing folder via the path bar; the backend validates it before starting |
| Toggles “do nothing” | Fixed in v1.1.0 — every toggle now applies instantly + persists. Hard‑refresh (`Ctrl+Shift+R`) if you still see the old UI |
| Update button seems dead | Fixed in v1.1.0 — it now shows Updating… → Updated ✓. Requires `app.py` running |
| Rename / Delete Account 404 | Fixed in v1.1.0 — backend now implements both endpoints |

---

## 📜 Changelog

### v1.1.0 — reliability + honest UI update

**Fixed — downloads**

- **Spotify fixed:** removed the fragile `Song.from_url` Python‑API import that crashed on newer `spotdl` versions; now uses the stable `python -m spotdl` CLI only, respects your **format + bitrate** (96–320k), mirrors progress to the app console, and saves history on success *and* failure.
- **Video fixed:** thumbnails are now conditional (`Download Thumbnail` toggle) instead of forced `EmbedThumbnail` (which used to fail whole downloads when FFmpeg/thumb was missing); **audio bitrate choice is respected** (`FFmpegExtractAudio` quality from your `320k/256k/…` pick); direct HLS/`.mp4` handling kept; `noplaylist` now honours the **Full Playlist** toggle.
- **Clear errors:** raw `yt‑dlp`/`spotdl` tracebacks are translated (`403`, private video, age‑restricted, DRM, timeout, missing FFmpeg…) in both the app console and terminal.

**Fixed — missing backend (frontend called them, server 404'd)**

- Added `POST /api/history/rename` (History ✏️ button works again).
- Added `POST /api/delete-account` (Settings → Delete Account works again).
- Fixed Settings updater row (it looked for `#sp-update-title`/`#sp-update-sub` that didn't exist — ids added, Updating…/Updated ✓ states visible).
- `/api/info` now also returns `version` + `ffmpeg_path`.

**Fixed — premium toggles (“didn't change anything”)**

| Toggle | Before | After |
|--------|--------|-------|
| Auto‑detect URL | Always auto‑switched options | OFF = badge only, your Mode/Format untouched |
| Download Thumbnail | Ignored | Sent as `thumb` → backend skips thumbnail steps |
| Full Playlist | Ignored (`"Playlist" in mode` only) | Sent as `playlist_all` → forces full‑playlist download |
| Hero Animations | Ignored | Toggles `body.no-anim`, kills/re‑enables animations + toast feedback |
| Console Log | Ignored | Toggles `body.hide-console`, hides/shows console + toast |
| Save Login Session | Partly worked (DOM race) | Uses settings state directly; session set/cleared reliably |

**Better Info (ⓘ)**

- Rebuilt from a 2‑line stub into a premium card: hero + version badge, live **App / yt‑dlp / FFmpeg** stats, *What it does* guide, supported‑source chips, **System status** rows (network URL, save folder), then Legal & Support.
- **What’s New** popup rewritten to describe these real changes and re‑shown once for existing users.

**Better terminal (`python app.py`)**

- Old: 6 plain lines, silent installs, zero download output.
- New: ASCII‑safe startup banner (version, Python, yt‑dlp, local + network URLs, FFmpeg status, data dir, how to read downloads), `[SETUP]` dependency lines, and per‑download logs: `[DL] NEW …`, `[YT-DLP]/[SPOTIFY] … Found / Downloading / DONE -> folder / FAILED: reason`, `[UPDATE]`, `[HIST]`, `[AUTH]` lines. Safe on Windows `cp1252` consoles.

**Docs**

- README rewritten: correct install (no phantom `requirements.txt`/`static/`/`templates/`), accurate settings table, endpoint list, expanded troubleshooting, and this changelog.

### v1.0.0 — initial release

- Flask + single‑file UI, auth, history, notifications, YouTube/Spotify/SoundCloud/TikTok/Instagram/Twitch support, HLS handling, settings panel shell, About/Terms/Privacy/Cookies modals.

---

## 🤝 Contributing

This is a personal self‑hosted project, but contributions are welcome!
If you find a bug or have a feature request, please open an issue or submit a pull request.

## 📄 License

Distributed under the MIT License. See the `LICENSE` file for more information.

## 🙌 Acknowledgements

- `yt‑dlp` – the powerhouse behind media extraction
- `spotdl` – for seamless Spotify audio
- `Flask` – the lightweight web framework
- `FFmpeg` – for audio/video processing

Made with ❤️ for a faster, cleaner download experience.
