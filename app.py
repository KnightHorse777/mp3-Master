from flask import Flask, request, send_file, render_template, jsonify
import yt_dlp
import os
import threading
from pathlib import Path

app = Flask(__name__)

# Find user's Downloads folder
DOWNLOAD_DIR = str(Path.home() / "Downloads")

# Global progress dictionary
progress_data = {
    "status": "idle",
    "downloaded_bytes": 0,
    "total_bytes": 0,
    "filename": ""
}

# Progress hook
def progress_hook(d):
    if d['status'] == 'downloading':
        progress_data["status"] = "downloading"
        progress_data["downloaded_bytes"] = d.get("downloaded_bytes", 0)
        # fallback to estimated size if total_bytes missing
        progress_data["total_bytes"] = d.get("total_bytes", d.get("total_bytes_estimate", 0))
        # ensure filename is always present
        title = d.get("info_dict", {}).get("title", "audio")
        progress_data["filename"] = title + ".mp3"

    elif d['status'] == 'finished':
        progress_data["status"] = "finished"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    url = request.form.get("url")
    if not url:
        return "❌ Please provide a YouTube URL"

    # Reset progress for new download
    progress_data.update({
        "status": "starting",
        "downloaded_bytes": 0,
        "total_bytes": 0,
        "filename": ""
    })

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "ffmpeg_location": r"C:\Shashank Shukla\mp3 convertor\ffmpeg\bin",  # adjust if needed
        "progress_hooks": [progress_hook],
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }

    def run_download():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        except Exception as e:
            progress_data["status"] = "error"
            progress_data["message"] = str(e)

    threading.Thread(target=run_download).start()
    return "✅ Download started"

@app.route("/progress")
def progress():
    return jsonify(progress_data)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
