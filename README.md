# AdMaster AI Studio (MVP)

A low-cost starter website for creating product ads from uploaded images/videos. It includes a responsive Arabic/English UI, local project form, preview, and a real FFmpeg MP4 render endpoint.

## Requirements
- Python 3.10+
- FFmpeg installed and available on PATH
- Optional: AI provider API key (not required for basic image-to-video motion render)

## Run locally
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:8000

## What works
- Upload a product image
- Enter product details and ad text
- Render an animated 9:16 MP4 with FFmpeg (pan/zoom, text overlay, music optional)
- Download the actual MP4 output

## Important
This MVP does NOT yet call a paid text-to-video provider. It creates real motion-video ads from uploaded images and uses FFmpeg for rendering. To add generated AI scenes, configure a provider in `providers.py` and implement its API integration. Never put API keys in frontend code.

## Android
The responsive website can be wrapped using Capacitor later. This package is a website MVP, not a prebuilt APK.
