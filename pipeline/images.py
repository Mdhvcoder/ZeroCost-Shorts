"""Free image generation using Hugging Face Inference API."""
from __future__ import annotations

import os
import time
from pathlib import Path

import requests

STYLE_SUFFIX = (
    ", cinematic digital illustration, detailed scene art, strong composition, "
    "professional youtube visual quality, no text, no captions, no watermark, no logos"
)

DEFAULT_NEGATIVE = (
    "blurry, low quality, watermark, logo, text, title, signature, ugly, grainy, "
    "gore, blood, nudity, child-unsafe"
)

HF_API_URL = "https://router.huggingface.co/hf-inference/models/black-forest-labs/FLUX.1-schnell"

def full_visual_prompt(scene: str, style_suffix: str | None = None) -> str:
    return f"{scene.strip()}{(style_suffix or STYLE_SUFFIX)}"

def save_scene_image(
    index: int,
    prompt: str,
    out_path: Path,
    *,
    width: int = 1024,
    height: int = 1024,
    negative: str = DEFAULT_NEGATIVE,
) -> tuple[str, str]:
    """Generate and save one image using Hugging Face. Returns (status, detail)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    api_key = os.environ.get("HF_TOKEN", "").strip()
    if not api_key:
        return "fail", "HF_TOKEN not set"

    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {"inputs": prompt + STYLE_SUFFIX}

    try:
        print(f"      Generating image {index} via Hugging Face...")
        resp = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
        if resp.status_code == 503:
            time.sleep(20)
            resp = requests.post(HF_API_URL, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        print(f"      Image {index} saved")
        return "ok", "huggingface"
    except Exception as e:
        return "fail", str(e)
