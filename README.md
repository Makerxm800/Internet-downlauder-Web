Create a virtual environment (recommended)

bash
python -m venv venv
source venv/bin/activate      # macOS/Linux
venv\Scripts\activate         # Windows
Install dependencies

bash
pip install -r requirements.txt
Install ffmpeg (if not already present)

macOS: brew install ffmpeg

Ubuntu/Debian: sudo apt install ffmpeg

Windows: winget install ffmpeg (or download from ffmpeg.org)

Start the server

bash
python app.py
Open your browser and go to:

text
http://localhost:5000
🖥️ Usage
Paste a URL into the main input field – the platform badge will appear automatically.

Select your format and quality from the animated dropdowns.

Click "Download Now" – progress is shown live.

Track everything in the History panel – re‑download, rename, or delete entries.

Customise your experience via the Settings panel (gear icon in the top bar).

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
text
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
