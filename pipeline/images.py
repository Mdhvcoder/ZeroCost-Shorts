"""Free image generation using AI Horde (anonymous, no API key)."""
from __future__ import annotations

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

HORDE_API = "https://aihorde.net/api/v2/generate/async"
HORDE_STATUS = "https://aihorde.net/api/v2/generate/status"

def full_visual_prompt(scene: str, style_suffix: str | None = None) -> str:
    return f"{scene.strip()}{(style_suffix or STYLE_SUFFIX)}"

def save_scene_image(
    index: int,
    prompt: str,
    out_path: Path,
    *,
    width: int = 512,
    height: int = 512,
    negative: str = DEFAULT_NEGATIVE,
) -> tuple[str, str]:
    """Generate one image via AI Horde (anonymous)."""
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    headers = {"apikey": "0000000000", "Client-Agent": "ZeroCostShorts:1.0"}
    payload = {
        "prompt": prompt + STYLE_SUFFIX,
        "params": {
            "width": width,
            "height": height,
            "steps": 20,
            "n": 1
        },
        "nsfw": False,
        "models": ["stable_diffusion"]
    }

    try:
        print(f"      Submitting image {index} to AI Horde...")
        resp = requests.post(HORDE_API, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        job_id = resp.json()["id"]

        # Poll for result
        for _ in range(40):
            time.sleep(6)
            status = requests.get(f"{HORDE_STATUS}/{job_id}", headers=headers, timeout=30)
            status.raise_for_status()
            data = status.json()
            if data.get("done"):
                img_url = data["generations"][0]["img"]
                img = requests.get(img_url, timeout=60)
                img.raise_for_status()
                out_path.write_bytes(img.content)
                print(f"      Image {index} saved")
                return "ok", "aihorde"
            if data.get("faulted"):
                return "fail", "AI Horde faulted"
        return "fail", "AI Horde timeout"
    except Exception as e:
        return "fail", str(e)
