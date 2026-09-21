#!/usr/bin/env python3
"""
IDLR — Internet Downloader
YouTube · Spotify · SoundCloud · Twitter · Instagram · TikTok and more
Fast · Private · Unlimited
"""
import subprocess, sys, os

APP_VERSION = "1.2.0"

def log(tag, msg):
    """Pretty timestamped terminal log, e.g. [12:01:44] [IDLR:DL] message."""
    import datetime as _dt
    ts = _dt.datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] [{tag}] {msg}"
    try:
        print(line, flush=True)
    except UnicodeEncodeError:
        print(line.encode("ascii", "replace").decode(), flush=True)

def pip(pkg):
    log("SETUP", f"Installing {pkg} ... (first run only)")
    subprocess.check_call([sys.executable,"-m","pip","install",pkg,"-q"],
                          stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    log("SETUP", f"Installed {pkg} OK")

log("SETUP", "Checking dependencies (flask, yt-dlp, static-ffmpeg, spotdl) ...")
for p,i in [("flask","flask"),("yt-dlp","yt_dlp"),("static-ffmpeg","static_ffmpeg"),("spotdl","spotdl")]:
    try:
        __import__(i)
        log("SETUP", f"  [OK] {p} already installed")
    except ImportError:
        pip(p)

from flask import Flask, request, jsonify, Response, send_from_directory
import yt_dlp, static_ffmpeg, shutil, json, hashlib, datetime, base64
import threading, uuid, re, time, socket, webbrowser

static_ffmpeg.add_paths()
FFMPEG = shutil.which("ffmpeg") or ""

# ── Storage ───────────────────────────────────────────────────────────────────
APP_DIR   = os.path.join(os.path.expanduser("~"), ".idlr_app")
ACCS_FILE = os.path.join(APP_DIR, "accounts.json")
HIST_FILE = os.path.join(APP_DIR, "history.json")
os.makedirs(APP_DIR, exist_ok=True)

def jload(p, d):
    try:
        with open(p) as f: return json.load(f)
    except: return d

def jsave(p, d):
    with open(p,"w") as f: json.dump(d, f, indent=2)

def hashpw(pw): return hashlib.sha256(pw.encode()).hexdigest()

def local_ip():
    try:
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("8.8.8.8",80)); ip=s.getsockname()[0]; s.close(); return ip
    except: return "localhost"

def is_spotify(url):
    return "spotify.com" in url or url.startswith("spotify:")

def is_hls_or_direct(url):
    """Direct HLS/m3u8 stream or direct video file URL"""
    u = url.lower().split("?")[0]
    return any(u.endswith(ext) for ext in (".m3u8",".m3u",".ts",".mp4",".mkv",".webm",".avi",".mov",".flv"))

def get_movie_opts(job, url, quality, fmt, savepath):
    """yt-dlp options tuned for movie/HLS sites"""
    q_map = {
        "Best (Max Quality)": "bestvideo+bestaudio/best",
        "4K":   "bestvideo[height<=2160]+bestaudio/best",
        "1440p":"bestvideo[height<=1440]+bestaudio/best",
        "1080p":"bestvideo[height<=1080]+bestaudio/best",
        "720p": "bestvideo[height<=720]+bestaudio/best",
        "480p": "bestvideo[height<=480]+bestaudio/best",
        "360p": "bestvideo[height<=360]+bestaudio/best",
    }
    opts = {
        "outtmpl": os.path.join(savepath, "%(title)s.%(ext)s"),
        "quiet": True, "no_warnings": True,
        "progress_hooks": [lambda d: _hook(job, d)],
        # HLS specific
        "hls_prefer_native": False,       # use ffmpeg for HLS (more reliable)
        "hls_use_mpegts": True,
        "allow_unplayable_formats": False,
        # Generic extractor — try hard to find video on any page
        "force_generic_extractor": False,
        "geo_bypass": True,
        # Better compat
        "socket_timeout": 30,
        "retries": 5,
        "fragment_retries": 10,
        "concurrent_fragment_downloads": 5,
        # Headers to look like a browser
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": url,
        },
    }
    if FFMPEG:
        opts["ffmpeg_location"] = os.path.dirname(FFMPEG)
    out_fmt = fmt if fmt in ("mp4","mkv","webm") else "mp4"
    opts["format"] = q_map.get(quality, "bestvideo+bestaudio/best")
    opts["merge_output_format"] = out_fmt
    return opts

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, template_folder=SCRIPT_DIR)
_jobs = {}

# ── Static ────────────────────────────────────────────────────────────────────
@app.route("/")
def index(): return send_from_directory(SCRIPT_DIR, "index.html")

@app.route("/favicon.svg")
def favicon(): return send_from_directory(SCRIPT_DIR, "favicon.svg")

# ── Auth ──────────────────────────────────────────────────────────────────────
def _user_resp(email, u):
    return jsonify(ok=True, name=u["name"], email=email,
                   username=u.get("username",""),
                   bio=u.get("bio",""),
                   avatar=u.get("avatar",""),
                   method=u.get("method","email"),
                   prefs=u.get("prefs",{}),
                   joined=u.get("joined",""))

@app.route("/api/register", methods=["POST"])
def register():
    d=request.json or {}
    accs=jload(ACCS_FILE,{})
    email=d.get("email","").strip().lower()
    pw=d.get("password",""); name=d.get("name","").strip()
    if not email or "@" not in email: return jsonify(error="Invalid email"),400
    if not pw or len(pw)<6: return jsonify(error="Password must be 6+ characters"),400
    if not name: return jsonify(error="Name required"),400
    if email in accs: return jsonify(error="Account already exists"),409
    accs[email]={"name":name,"pw_hash":hashpw(pw),"joined":str(datetime.date.today()),
                 "method":"email","prefs":{},"username":"","bio":"","avatar":""}
    jsave(ACCS_FILE,accs)
    return _user_resp(email, accs[email])

@app.route("/api/login", methods=["POST"])
def login():
    d=request.json or {}
    accs=jload(ACCS_FILE,{})
    email=d.get("email","").strip().lower(); pw=d.get("password","")
    if email not in accs: return jsonify(error="No account with this email"),404
    if accs[email].get("pw_hash")!=hashpw(pw): return jsonify(error="Wrong password"),401
    return _user_resp(email, accs[email])

@app.route("/api/google-login", methods=["POST"])
def google_login():
    d=request.json or {}
    accs=jload(ACCS_FILE,{})
    email=d.get("email","").strip().lower()
    if not email or "@" not in email: return jsonify(error="Invalid Gmail"),400
    if email not in accs:
        gname=email.split("@")[0].replace("."," ").title()
        accs[email]={"name":gname,"pw_hash":"","joined":str(datetime.date.today()),
                     "method":"google","prefs":{},"username":"","bio":"","avatar":""}
        jsave(ACCS_FILE,accs)
    return _user_resp(email, accs[email])

# ── Profile update ────────────────────────────────────────────────────────────
@app.route("/api/profile", methods=["POST"])
def update_profile():
    d=request.json or {}
    email=d.get("user","").strip().lower()
    accs=jload(ACCS_FILE,{})
    if email not in accs: return jsonify(error="User not found"),404
    u=accs[email]
    if "name"     in d and d["name"].strip():     u["name"]     = d["name"].strip()[:40]
    if "username" in d:                            u["username"] = d["username"].strip()[:24]
    if "bio"      in d:                            u["bio"]      = d["bio"].strip()[:160]
    if "avatar"   in d:                            u["avatar"]   = d["avatar"]  # base64 data-url
    jsave(ACCS_FILE,accs)
    return _user_resp(email, u)

# ── Prefs ─────────────────────────────────────────────────────────────────────
@app.route("/api/prefs", methods=["POST"])
def save_prefs():
    d=request.json or {}
    email=d.get("user","").strip().lower(); prefs=d.get("prefs",{})
    accs=jload(ACCS_FILE,{})
    if email not in accs: return jsonify(error="User not found"),404
    accs[email]["prefs"]=prefs; jsave(ACCS_FILE,accs)
    return jsonify(ok=True)

# ── History ───────────────────────────────────────────────────────────────────
@app.route("/api/history")
def get_history():
    email=request.args.get("user","")
    hist=jload(HIST_FILE,[])
    return jsonify([h for h in hist if h.get("user")==email][-80:])

@app.route("/api/history/clear", methods=["DELETE"])
def clear_history():
    email=request.args.get("user","")
    jsave(HIST_FILE,[h for h in jload(HIST_FILE,[]) if h.get("user")!=email])
    return jsonify(ok=True)

@app.route("/api/history/remove", methods=["DELETE"])
def remove_history_item():
    d=request.json or {}
    email=d.get("user",""); url=d.get("url","")
    hist=[h for h in jload(HIST_FILE,[])
          if not(h.get("user")==email and h.get("url")==url)]
    jsave(HIST_FILE,hist)
    return jsonify(ok=True)

# ── Spotify download via spotdl ───────────────────────────────────────────────
def _parse_bitrate(quality, default="320k"):
    """Accept '320k' / '256k' / ... or 'Best (Max Quality)' -> default."""
    import re as _re
    m = _re.search(r"(\d+)\s*k", str(quality or ""))
    if m:
        kbps = max(64, min(320, int(m.group(1))))
        return f"{kbps}k", str(kbps)
    return default, default.replace("k", "")

def _spotify_run(job, url, savepath, user, fmt, quality="320k", job_id="?"):
    """Download Spotify track/album/playlist using the spotdl CLI.

    Uses the CLI only (the Python API changes between spotdl versions,
    so importing Song/Spotdl directly is fragile and used to crash this).
    """
    os.makedirs(savepath, exist_ok=True)
    log("SPOTIFY", f"[{job_id}] {url}")
    log("SPOTIFY", f"[{job_id}] Target folder: {savepath}")
    job["log"].append({"t":"Detected Spotify link — using spotdl…","c":"dim"})
    job["status"]="downloading"

    title = url
    thumb = ""

    audio_fmt = fmt if fmt in ("mp3","m4a","opus","ogg","flac") else "mp3"
    bitrate, _kbps = _parse_bitrate(quality, "320k")
    log("SPOTIFY", f"[{job_id}] Format={audio_fmt} bitrate={bitrate}")

    # Light metadata attempt (non-fatal): prettify the title from the URL.
    try:
        if "track" in url or "album" in url or "playlist" in url:
            slug = url.split("?")[0].rstrip("/").split("/")[-1][:60]
            if slug:
                title = "Spotify — " + slug
                job["title"] = title
    except Exception:
        pass

    try:
        cmd = [sys.executable, "-m", "spotdl",
               "--output", savepath,
               "--format", audio_fmt,
               "--bitrate", bitrate,
               url]
        log("SPOTIFY", f"[{job_id}] Running: python -m spotdl --format {audio_fmt} --bitrate {bitrate} ...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
        out = (result.stdout or "") + "\n" + (result.stderr or "")
        # Mirror meaningful lines to the in-app console + terminal.
        shown = 0
        for line in out.split("\n"):
            s = line.strip()
            if not s:
                continue
            if any(k in s for k in ("Downloaded", "Skipping", "Found", "Searching")):
                job["log"].append({"t": s[:160], "c":"ok"})
                log("SPOTIFY", f"[{job_id}] {s[:160]}")
                shown += 1
            elif any(k in s for k in ("Error", "Failed", "Traceback", "WARNING")):
                job["log"].append({"t": s[:160], "c":"err"})
                log("SPOTIFY", f"[{job_id}] !! {s[:200]}")
                shown += 1
            if shown > 30:
                break

        ok = result.returncode == 0 or "Downloaded" in out
        if ok:
            job.update({"status":"done","progress":100,"done":True})
            job["log"].append({"t":f"✓ Spotify download saved to {savepath}","c":"ok"})
            log("SPOTIFY", f"[{job_id}] DONE -> {savepath}")
            _save_hist(user, url, title, thumb, "Audio Only", quality, audio_fmt, "done")
        else:
            tail = "\n".join([l for l in out.split("\n") if l.strip()][-6:])
            log("SPOTIFY", f"[{job_id}] FAILED (exit {result.returncode})")
            raise Exception(_friendly_dl_error(tail or "spotdl failed — is the link public?"))
    except subprocess.TimeoutExpired:
        log("SPOTIFY", f"[{job_id}] FAILED — timed out after 15 minutes")
        raise Exception("Download timed out after 15 minutes")

def _friendly_dl_error(raw):
    """Turn raw yt-dlp/spotdl errors into short human-readable messages."""
    s = (raw or "").strip().replace("\n", " ")
    low = s.lower()
    if "video unavailable" in low or "private video" in low:
        return "This video is private or unavailable."
    if "age" in low and "sign in" in low:
        return "Age-restricted video — sign-in required, cannot download."
    if "403" in low or "forbidden" in low:
        return "Source blocked the download (403). Update yt-dlp in Settings and retry."
    if "404" in low or "not found" in low:
        return "Link not found (404). Check the URL."
    if "unsupported url" in low or "no video formats found" in low:
        return "No downloadable video found at this URL."
    if "timed out" in low or "timeout" in low:
        return "Connection timed out. Check your internet and retry."
    if "ffmpeg" in low and ("not found" in low or "not installed" in low):
        return "FFmpeg is missing — install it and restart IDLR."
    if "copyright" in low or "drm" in low:
        return "This content is DRM-protected and cannot be downloaded."
    if not s:
        return "Download failed for an unknown reason."
    return s[:220]

# ── Generic yt-dlp download ───────────────────────────────────────────────────
def _ytdlp_run(job, url, mode, quality, fmt, savepath, user,
               want_thumb=True, playlist_all=False, job_id="?"):
    q_map={
        "Best (Max Quality)":"bestvideo+bestaudio/best",
        "4K":   "bestvideo[height<=2160]+bestaudio/best",
        "8K":   "bestvideo[height<=4320]+bestaudio/best",
        "1440p":"bestvideo[height<=1440]+bestaudio/best",
        "1080p":"bestvideo[height<=1080]+bestaudio/best",
        "720p": "bestvideo[height<=720]+bestaudio/best",
        "480p": "bestvideo[height<=480]+bestaudio/best",
        "360p": "bestvideo[height<=360]+bestaudio/best",
        "240p": "bestvideo[height<=240]+bestaudio/best",
        "144p": "bestvideo[height<=144]+bestaudio/best",
    }
    os.makedirs(savepath, exist_ok=True)
    log("YT-DLP", f"[{job_id}] {url}")
    log("YT-DLP", f"[{job_id}] mode={mode} quality={quality} format={fmt} thumb={'on' if want_thumb else 'off'} playlist_all={'on' if playlist_all else 'off'}")
    log("YT-DLP", f"[{job_id}] Target folder: {savepath}")
    if not FFMPEG:
        job["log"].append({"t":"⚠ FFmpeg not found — merging/MP3 may fail. Install FFmpeg.","c":"err"})
        log("YT-DLP", f"[{job_id}] WARNING: FFmpeg not found on PATH")

    # Use movie-grade opts for all downloads (HLS support, browser headers)
    opts = get_movie_opts(job, url, quality, fmt, savepath)
    is_playlist_mode = "Playlist" in mode
    opts["noplaylist"] = not (is_playlist_mode or playlist_all)

    is_audio = "Audio" in mode or fmt in ("mp3","m4a","flac","wav","opus")
    if is_audio:
        ext = fmt if fmt in ("mp3","m4a","flac","wav","opus") else "mp3"
        _br, kbps = _parse_bitrate(quality, "320k")
        opts["format"] = "bestaudio/best"
        opts.pop("merge_output_format", None)
        opts["postprocessors"] = [
            {"key":"FFmpegExtractAudio","preferredcodec":ext,"preferredquality":kbps},
        ]
        if want_thumb:
            opts["postprocessors"].append({"key":"EmbedThumbnail"})
            opts["writethumbnail"] = True
        else:
            opts["writethumbnail"] = False
    else:
        opts["format"] = q_map.get(quality, "bestvideo+bestaudio/best")
        opts["merge_output_format"] = fmt if fmt in ("mp4","mkv","webm") else "mp4"
        if want_thumb:
            opts["writethumbnail"] = True
            opts["postprocessors"] = [{"key":"EmbedThumbnail"}]
        else:
            opts["writethumbnail"] = False
            opts["postprocessors"] = []

    # If it's a direct HLS/m3u8 URL, force ffmpeg concat
    if is_hls_or_direct(url):
        opts["format"] = "best"
        opts["merge_output_format"] = "mp4"
        job["log"].append({"t":"🎬 Direct stream detected — using HLS downloader","c":"dim"})

    title = url; thumb = ""
    try:
        # Try to get metadata first
        log("YT-DLP", f"[{job_id}] Fetching title/thumbnail ...")
        meta_opts = {
            "quiet":True,"no_warnings":True,
            "http_headers": opts.get("http_headers",{}),
            "geo_bypass": True,
            "socket_timeout": 20,
        }
        with yt_dlp.YoutubeDL(meta_opts) as y:
            try:
                info = y.extract_info(url, download=False)
                title = (info.get("title") or info.get("webpage_title") or url)[:80]
                thumb = info.get("thumbnail","")
                # For movies/series: try to get better poster
                if not thumb and info.get("thumbnails"):
                    thumb = info["thumbnails"][-1].get("url","")
                job["title"] = title
                job["thumb"] = thumb
                job["log"].append({"t": title, "c":"dim"})
                log("YT-DLP", f"[{job_id}] Found: {title[:80]}")
            except Exception as me:
                job["log"].append({"t": f"Metadata: {_friendly_dl_error(str(me))[:90]}","c":"dim"})
                log("YT-DLP", f"[{job_id}] Metadata lookup failed: {str(me)[:120]}")

        job["status"] = "downloading"
        log("YT-DLP", f"[{job_id}] Downloading ...")
        with yt_dlp.YoutubeDL(opts) as y:
            y.download([url])

        job.update({"status":"done","progress":100,"done":True})
        job["log"].append({"t": f"✓ Saved to {savepath}","c":"ok"})
        log("YT-DLP", f"[{job_id}] DONE -> {savepath}")
        _save_hist(user, url, title, thumb, mode, quality, fmt, "done")

    except Exception as e:
        err_msg = _friendly_dl_error(str(e))
        job.update({"status":"error","error":err_msg,"done":True})
        job["log"].append({"t": f"✗ {err_msg}","c":"err"})
        log("YT-DLP", f"[{job_id}] FAILED: {err_msg}")
        _save_hist(user, url, title, thumb, mode, quality, fmt, "error")

def _save_hist(user, url, title, thumb, mode, quality, fmt, status):
    hist=jload(HIST_FILE,[])
    entry={"user":user,"url":url,"title":title,"thumb":thumb,"mode":mode,
           "quality":quality,"format":fmt,"status":status,
           "date":datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}
    hist=[h for h in hist if not(h.get("user")==user and h.get("url")==url)]
    hist.append(entry)
    jsave(HIST_FILE,hist)

# ── Download endpoint ─────────────────────────────────────────────────────────
@app.route("/api/download", methods=["POST"])
def start_download():
    d=request.json or {}
    url=d.get("url","").strip(); mode=d.get("mode","Video")
    quality=d.get("quality","Best (Max Quality)"); fmt=d.get("format","mp4")
    savepath=d.get("path","").strip() or os.path.join(os.path.expanduser("~"),"Downloads")
    user=d.get("user","")
    # Settings toggles forwarded by the frontend (default = old behaviour)
    want_thumb = d.get("thumb", True)
    if isinstance(want_thumb, str):
        want_thumb = want_thumb.lower() not in ("0","false","no","off")
    playlist_all = d.get("playlist_all", False)
    if isinstance(playlist_all, str):
        playlist_all = playlist_all.lower() in ("1","true","yes","on")
    if not url: return jsonify(error="No URL"),400
    if not os.path.isdir(savepath):
        try: os.makedirs(savepath, exist_ok=True)
        except Exception: return jsonify(error=f"Save folder not writable: {savepath}"),400

    jid=str(uuid.uuid4())[:8]
    _jobs[jid]={"status":"starting","progress":0,"speed":"","eta":"",
                "log":[],"title":"","thumb":"","error":None,"done":False}
    log("DL", f"[{jid}] NEW user={user or 'guest'} mode={mode} quality={quality} format={fmt}")
    log("DL", f"[{jid}] URL: {url[:140]}")

    def run():
        job=_jobs[jid]
        try:
            if is_spotify(url):
                _spotify_run(job, url, savepath, user, fmt, quality, jid)
            else:
                _ytdlp_run(job, url, mode, quality, fmt, savepath, user,
                           want_thumb, playlist_all, jid)
        except Exception as e:
            msg = _friendly_dl_error(str(e))
            job.update({"status":"error","error":msg,"done":True})
            job["log"].append({"t":f"✗ {msg}","c":"err"})
            log("DL", f"[{jid}] FAILED: {msg}")
            try: _save_hist(user, url, job.get("title") or url, job.get("thumb",""),
                            mode, quality, fmt, "error")
            except Exception: pass

    threading.Thread(target=run, daemon=True).start()
    return jsonify(job_id=jid)

def _hook(job, d):
    if d["status"]=="downloading":
        raw=d.get("_percent_str","0%").strip()
        try: pct=float(re.sub(r"[^\d.]","",raw) or 0)
        except ValueError: pct=0
        job.update({"progress":pct,"speed":d.get("_speed_str","").strip(),
                    "eta":d.get("_eta_str","").strip()})
    elif d["status"]=="finished":
        job["status"]="merging"
        job["log"].append({"t":"Merging video + audio…","c":"dim"})

@app.route("/api/progress/<jid>")
def progress(jid):
    def stream():
        ll=0
        while True:
            job=_jobs.get(jid)
            if not job: yield f"data:{json.dumps({'error':'not found'})}\n\n"; break
            new=job["log"][ll:]; ll=len(job["log"])
            yield f"data:{json.dumps({'status':job['status'],'progress':job['progress'],'speed':job['speed'],'eta':job['eta'],'title':job['title'],'thumb':job.get('thumb',''),'logs':new,'done':job['done'],'error':job['error']})}\n\n"
            if job["done"]: break
            time.sleep(0.3)
    return Response(stream(),mimetype="text/event-stream",
                    headers={"Cache-Control":"no-cache","X-Accel-Buffering":"no"})

@app.route("/api/preview", methods=["POST"])
def preview_url():
    """Fetch title + thumbnail from any URL using yt-dlp (no download)"""
    d = request.json or {}
    url = d.get("url","").strip()
    if not url: return jsonify(error="No URL"),400
    try:
        meta_opts = {
            "quiet":True,"no_warnings":True,"skip_download":True,
            "socket_timeout":15,"retries":2,
            "http_headers":{
                "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0.0.0 Safari/537.36",
                "Referer": url,
            },
            "geo_bypass":True,
        }
        with yt_dlp.YoutubeDL(meta_opts) as y:
            info = y.extract_info(url, download=False)
            title = (info.get("title") or info.get("webpage_title") or "")[:120]
            thumb = info.get("thumbnail","")
            if not thumb and info.get("thumbnails"):
                # pick highest resolution thumbnail
                thumbs = sorted(info["thumbnails"], key=lambda t: t.get("width",0) or t.get("preference",0), reverse=True)
                thumb = thumbs[0].get("url","") if thumbs else ""
            duration = info.get("duration")
            uploader = info.get("uploader") or info.get("channel") or ""
            return jsonify(ok=True, title=title, thumb=thumb,
                           duration=duration, uploader=uploader)
    except Exception as e:
        # Still return partial info
        return jsonify(ok=False, title="", thumb="", error=str(e)[:200])

@app.route("/api/info")
def info():
    return jsonify(ytdlp=yt_dlp.version.__version__,
                   ffmpeg=bool(FFMPEG),
                   ffmpeg_path=FFMPEG,
                   version=APP_VERSION,
                   network=f"http://{local_ip()}:5000")

@app.route("/api/history/rename", methods=["POST"])
def rename_history_item():
    """Rename a history entry — called by the ✏️ button in History."""
    d = request.json or {}
    email = d.get("user",""); url = d.get("url","")
    new_title = (d.get("newTitle") or d.get("new_title") or "").strip()[:120]
    if not email or not url: return jsonify(error="Missing user or url"),400
    if not new_title: return jsonify(error="Title cannot be empty"),400
    hist = jload(HIST_FILE, [])
    found = False
    for h in hist:
        if h.get("user")==email and h.get("url")==url:
            h["title"] = new_title
            found = True
    if not found: return jsonify(error="Entry not found"),404
    jsave(HIST_FILE, hist)
    log("HIST", f"Renamed entry for {email}: {new_title[:60]}")
    return jsonify(ok=True)

@app.route("/api/delete-account", methods=["POST"])
def delete_account():
    """Permanently delete an account + its history — called from Settings."""
    d = request.json or {}
    email = (d.get("user") or "").strip().lower()
    if not email: return jsonify(error="Missing user"),400
    accs = jload(ACCS_FILE, {})
    if email not in accs: return jsonify(error="Account not found"),404
    del accs[email]
    jsave(ACCS_FILE, accs)
    hist = [h for h in jload(HIST_FILE,[]) if h.get("user")!=email]
    jsave(HIST_FILE, hist)
    log("AUTH", f"Deleted account: {email}")
    return jsonify(ok=True)

@app.route("/api/update-ytdlp", methods=["POST"])
def update_ytdlp():
    log("UPDATE", "Updating yt-dlp + spotdl to latest ...")
    try:
        out = subprocess.check_output([sys.executable,"-m","pip","install","--upgrade","yt-dlp","spotdl"],
                                 stderr=subprocess.STDOUT, text=True)
        import importlib; importlib.reload(yt_dlp)
        msg = f"Updated! yt-dlp v{yt_dlp.version.__version__}"
        log("UPDATE", msg + " — spotdl upgraded too")
        return jsonify(ok=True,msg=msg)
    except subprocess.CalledProcessError as e:
        tail = (e.output or "")[-400:]
        log("UPDATE", f"FAILED: {tail[:200]}")
        return jsonify(ok=False,msg=_friendly_dl_error(tail))
    except Exception as e:
        log("UPDATE", f"FAILED: {e}")
        return jsonify(ok=False,msg=str(e))

if __name__=="__main__":
    ip=local_ip()
    import platform as _pf
    def _p(s):
        try: print(s, flush=True)
        except UnicodeEncodeError: print(s.encode("ascii","replace").decode(), flush=True)
    _p("")
    _p("==========================================================")
    _p("  IDLR -- Internet Downloader")
    _p(f"  v{APP_VERSION} | Python {_pf.python_version()} | yt-dlp v{yt_dlp.version.__version__}")
    _p("  YouTube | Spotify | SoundCloud | TikTok | 1000+ sites")
    _p("==========================================================")
    _p(f"  > Local      http://localhost:5000")
    _p(f"  > Network    http://{ip}:5000   (share on your Wi-Fi)")
    _p(f"  > FFmpeg     {'FOUND ' + FFMPEG if FFMPEG else 'NOT FOUND -- install FFmpeg for MP3/merging'}")
    _p(f"  > Data       {APP_DIR}  (accounts + history stay on this PC)")
    _p("==========================================================")
    _p("  Downloads:")
    _p("    - Paste a link in the app -> watch progress HERE + in the app console")
    _p("    - Statuses: [YT-DLP] video / [SPOTIFY] audio / [UPDATE] updater")
    _p("    - DONE = saved to your Save Location | FAILED = reason shown here")
    _p("==========================================================")
    _p("  Keep this window OPEN while using the app. Press Ctrl+C to stop.\n")
    threading.Timer(1.4,lambda:webbrowser.open("http://localhost:5000")).start()
    app.run(host="0.0.0.0",port=5000,debug=False,threaded=True)
