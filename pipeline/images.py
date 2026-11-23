"""Free image generation using Pollinations.ai (no API key needed)."""
from __future__ import annotations

import os
import time
import urllib.parse
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


def full_visual_prompt(scene: str, style_suffix: str | None = None) -> str:
    """Combine the scene description with a channel-specific style suffix."""
    return f"{scene.strip()}{(style_suffix or STYLE_SUFFIX)}"


def save_scene_image(
    index: int,
    prompt: str,
    out_path: Path,
    *,
    width: int = 1080,
    height: int = 1920,
    negative: str = DEFAULT_NEGATIVE,
) -> tuple[str, str]:
    """Generate and save one image using free Pollinations. Returns (status, detail)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    full_prompt = prompt + STYLE_SUFFIX
    encoded = urllib.parse.quote(full_prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&nologo=true&model=flux&seed={int(time.time()) + index}"
    )

    try:
        print(f"      Generating image {index} via Pollinations...")
        resp = requests.get(url, timeout=90)
        resp.raise_for_status()
        out_path.write_bytes(resp.content)
        print(f"      Image {index} saved")
        return "ok", "pollinations"
    except Exception as e:
        return "fail", str(e)
