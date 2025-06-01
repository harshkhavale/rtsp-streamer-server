# utils.py (or inside your views.py if you prefer)
import os
from urllib.parse import quote

def generate_ws_url(rtsp_url):
    ws_base_url = os.getenv("WS_BASE_URL", "ws://localhost:8000")
    encoded_url = quote(rtsp_url, safe='')
    return f"{ws_base_url}/ws/stream/?url={encoded_url}"
