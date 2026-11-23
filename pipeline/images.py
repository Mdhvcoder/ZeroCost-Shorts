"""Free image generation using Pollinations.ai with retries."""
from __future__ import annotations

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
    """Generate and save one image using Pollinations with retries."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    full_prompt = prompt + STYLE_SUFFIX
    encoded = urllib.parse.quote(full_prompt)
    url = (
        f"https://image.pollinations.ai/prompt/{encoded}"
        f"?width={width}&height={height}&nologo=true&model=flux&seed={int(time.time()) + index}"
    )

    for attempt in range(1, 4):
        try:
            print(f"      Generating image {index} via Pollinations (attempt {attempt})...")
            resp = requests.get(url, timeout=90)
            if resp.status_code == 402:
                print(f"      Rate limited, waiting 30s...")
                time.sleep(30)
                continue
            resp.raise_for_status()
            out_path.write_bytes(resp.content)
            print(f"      Image {index} saved")
            return "ok", "pollinations"
        except Exception as e:
            if attempt == 3:
                return "fail", str(e)
            time.sleep(10)
    return "fail", "max retries exceeded"
