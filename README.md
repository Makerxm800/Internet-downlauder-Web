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

2- Create a virtual environment (recommended) python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows


3- Install dependencies pip install -r requirements.txt


4- Install ffmpeg (if not already present)

macOS: brew install ffmpeg

Ubuntu/Debian: sudo apt install ffmpeg

Windows: winget install ffmpeg (or download from ffmpeg.org)

5- Start the server python app.py

6- Open your browser and go to: http://localhost:5000

🖥️ Usage
1 Paste a URL into the main input field – the platform badge will appear automatically.

2 Select your format and quality from the animated dropdowns.

3 Click "Download Now" – progress is shown live.

4 Track everything in the History panel – re‑download, rename, or delete entries.

5 Customise your experience via the Settings panel (gear icon in the top bar).

⚙️ Configuration
All settings can be adjusted either from the in‑app Settings panel or by editing the ~/.idlr_app/ config files (created automatically on first run).

Setting	Default	Description
Download folder	~/Downloads	Where finished files are saved
Default quality	Best (Max Quality)	Fallback if no quality is chosen
Auto‑detect URL	On	Automatically sets options based on the pasted link
Download thumbnail	On	Saves cover art alongside audio files
Full playlist download	Off	Downloads entire playlists in one go
Hero animations	On	Enables the animated hero title on load
Console log	On	Shows live download output below the progress bar
Save login session	On	Keeps you signed in across restarts
Note: All data (history, accounts, settings) is stored locally in ~/.idlr_app/. No data is ever sent anywhere.

🗂️ Project Structure
idlr/
├── app.py                 # Flask backend entry point
├── static/                # Static assets (CSS, JS, images)
├── templates/             # HTML templates
│   └── index.html
├── downloads/             # Downloaded media (gitignored)
├── requirements.txt       # Python dependencies
└── README.md              # This file

🐛 Troubleshooting
Issue	Solution
ffmpeg not found	Ensure ffmpeg is installed and on your PATH. Restart your terminal after installing.
YouTube downloads fail (403)	Try updating yt‑dlp via the Settings panel or run pip install --upgrade yt-dlp.
Spotify downloads are slow	spotdl relies on YouTube matches – obscure tracks may take longer.
Thumbnails not showing	Some platforms serve thumbnails over HLS; a manual refresh option is planned.
🤝 Contributing
This is a personal self‑hosted project, but contributions are welcome!
If you find a bug or have a feature request, please open an issue or submit a pull request.

📄 License
Distributed under the MIT License. See the LICENSE file for more information.

🙌 Acknowledgements
yt‑dlp – the powerhouse behind media extraction

spotdl – for seamless Spotify audio

Flask – the lightweight web framework

FFmpeg – for audio/video processing

Made with ❤️ for a faster, cleaner download experience.
