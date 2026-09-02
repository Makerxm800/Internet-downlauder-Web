# ⚡ IDLR — Internet Downloader

**Your personal, self‑hosted media download hub.**  
Paste any link, and IDLR grabs the video or audio you want — no ads, no redirects, no third‑party uploads.  
Everything runs locally on your machine.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![yt‑dlp](https://img.shields.io/badge/yt--dlp-latest-orange)
![spotdl](https://img.shields.io/badge/spotdl-latest-brightgreen)

---

## ✨ Features

- 🌐 **1000+ supported sites** via `yt‑dlp` – YouTube, TikTok, Instagram, Twitch, and more  
- 🎵 **Spotify audio** – dedicated handling for tracks and playlists via `spotdl`  
- 🔍 **Live URL detection** – paste a link and the UI instantly recognises the platform  
- 🖼️ **Thumbnail preview** – see what you’re downloading before you commit  
- ⚙️ **Slide‑in settings panel** – adjust download location, quality, and defaults without leaving the page  
- 📋 **Bulk history management** – search, select, re‑download, or delete entries in one go  
- 🔒 **100% private** – nothing leaves your network except the request to the source site  

---

## 🧩 Supported Platforms

| Platform | Video | Audio |
|----------|:-----:|:-----:|
| YouTube  | ✅    | ✅    |
| Spotify  | —     | ✅    |
| SoundCloud| —    | ✅    |
| TikTok   | ✅    | ✅    |
| Twitter/X| ✅    | ✅    |
| Instagram| ✅    | ✅    |
| Twitch   | ✅    | ✅    |
| Vimeo    | ✅    | ✅    |
| Facebook | ✅    | ✅    |
| Reddit   | ✅    | ✅    |
| Dailymotion| ✅  | ✅    |
| HLS streams| ✅  | ✅    |
| + 1000 more via `yt‑dlp` | ✅ | ✅ |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or newer  
- `ffmpeg` installed and available on your system `PATH` (required for audio extraction and merging)  

### Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/yourusername/idlr.git
   cd idlr
