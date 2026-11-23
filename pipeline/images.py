"""Stock image generation using Pixabay free API."""
from __future__ import annotations

import os
import random
from pathlib import Path

import requests

STYLE_SUFFIX = ""  # Not needed for stock search

DEFAULT_NEGATIVE = ""

def full_visual_prompt(scene: str, style_suffix: str | None = None) -> str:
    # Use the scene description as search keywords
    return scene.strip()

def save_scene_image(
    index: int,
    prompt: str,
    out_path: Path,
    *,
    width: int = 1280,
    height: int = 720,
    negative: str = "",
) -> tuple[str, str]:
    """Download a relevant stock image from Pixabay."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    api_key = os.environ.get("PIXABAY_API_KEY", "").strip()
    if not api_key:
        return "fail", "PIXABAY_API_KEY not set"

    # Clean the prompt for search
    query = prompt.split(",")[0].strip()[:80]
    url = "https://pixabay.com/api/"
    params = {
        "key": api_key,
        "q": query,
        "image_type": "photo",
        "orientation": "horizontal",
        "per_page": 20,
        "safesearch": "true"
    }

    try:
        print(f"      Searching Pixabay for: {query}")
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        hits = data.get("hits", [])
        if not hits:
            return "fail", "No images found on Pixabay"

        # Pick a random image from results
        hit = random.choice(hits)
        img_url = hit.get("largeImageURL") or hit.get("webformatURL")
        if not img_url:
            return "fail", "No image URL"

        img_resp = requests.get(img_url, timeout=60)
        img_resp.raise_for_status()
        out_path.write_bytes(img_resp.content)
        print(f"      Image {index} saved from Pixabay")
        return "ok", "pixabay"
    except Exception as e:
        return "fail", str(e)
