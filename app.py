import os, uuid, shutil, subprocess
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory, render_template
from werkzeug.utils import secure_filename

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
OUTPUTS = BASE / "outputs"
UPLOADS.mkdir(exist_ok=True)
OUTPUTS.mkdir(exist_ok=True)
app = Flask(__name__, static_folder="static", template_folder="templates")
app.config["MAX_CONTENT_LENGTH"] = 100 * 1024 * 1024
ALLOWED = {".png", ".jpg", ".jpeg", ".webp"}

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/health")
def health():
    ffmpeg = shutil.which("ffmpeg")
    return jsonify({"ok": True, "ffmpeg_available": bool(ffmpeg)})

@app.post("/api/render")
def render_ad():
    if not shutil.which("ffmpeg"):
        return jsonify({"error": "FFmpeg is not installed on the server. Install FFmpeg and restart the app."}), 503
    image = request.files.get("image")
    if not image or not image.filename:
        return jsonify({"error": "Upload a product image first."}), 400
    ext = Path(secure_filename(image.filename)).suffix.lower()
    if ext not in ALLOWED:
        return jsonify({"error": "Supported image formats: PNG, JPG, JPEG, WEBP."}), 400

    job_id = uuid.uuid4().hex[:12]
    source = UPLOADS / f"{job_id}{ext}"
    output = OUTPUTS / f"ad_{job_id}.mp4"
    image.save(source)

    headline = (request.form.get("headline") or "اكتشف المنتج الآن").strip()[:70]
    subline = (request.form.get("subline") or "جودة تستحق التجربة").strip()[:90]
    duration = request.form.get("duration", "15")
    try:
        duration = max(5, min(30, int(duration)))
    except ValueError:
        duration = 15

    # Use drawtext safely by writing text into a file; use UTF-8 text files.
    headline_file = UPLOADS / f"{job_id}_headline.txt"
    subline_file = UPLOADS / f"{job_id}_subline.txt"
    headline_file.write_text(headline, encoding="utf-8")
    subline_file.write_text(subline, encoding="utf-8")

    # Font selection varies by OS; DejaVu Sans is common on Linux. Arabic shaping depends
    # on installed fonts and FFmpeg build. Users can install Noto Naskh Arabic for best results.
    font_candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
        "C:/Windows/Fonts/arial.ttf"
    ]
    font = next((f for f in font_candidates if os.path.exists(f)), None)
    font_arg = f":fontfile='{font.replace(chr(92), '/')}'" if font else ""
    def esc_path(p):
        return str(p).replace("\\", "/").replace(":", r"\:").replace("'", r"\'")
    # Slow zoom gives a cinematic motion effect from a single image.
    vf = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        f"zoompan=z='min(zoom+0.0008,1.12)':d={duration*30}:s=1080x1920:fps=30,"
        "eq=saturation=1.08:contrast=1.04,"
        f"drawtext=textfile='{esc_path(headline_file)}'{font_arg}:fontcolor=white:fontsize=58:"
        "borderw=3:bordercolor=black@0.65:x=(w-text_w)/2:y=h*0.70,"
        f"drawtext=textfile='{esc_path(subline_file)}'{font_arg}:fontcolor=white:fontsize=36:"
        "borderw=2:bordercolor=black@0.65:x=(w-text_w)/2:y=h*0.76"
    )
    cmd = [
        "ffmpeg", "-y", "-loop", "1", "-i", str(source),
        "-vf", vf, "-t", str(duration), "-r", "30",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(output)
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=240)
        if proc.returncode != 0:
            return jsonify({"error": "Render failed. Check that FFmpeg includes libx264 and drawtext.", "details": proc.stderr[-1600:]}), 500
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Rendering took too long. Try a shorter video or smaller image."}), 504
    finally:
        for p in (source, headline_file, subline_file):
            try: p.unlink(missing_ok=True)
            except Exception: pass

    return jsonify({"ok": True, "download_url": f"/outputs/{output.name}", "filename": output.name})

@app.get("/outputs/<path:filename>")
def download_output(filename):
    return send_from_directory(OUTPUTS, filename, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8000")), debug=False)
