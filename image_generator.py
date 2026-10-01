import os
import re
import uuid
from pathlib import Path
from typing import Optional
from PIL import Image, ImageDraw, ImageFont
from ..config import STATIC_PANELS, SD_MODEL_ID, MOCK_MODE

# Lazy-loaded pipeline
_pipe = None

def _get_pipeline():
    global _pipe
    if _pipe is not None:
        return _pipe
    try:
        from diffusers import StableDiffusionPipeline
        import torch
        print(f"[ImageGen] Loading {SD_MODEL_ID}...")
        _pipe = StableDiffusionPipeline.from_pretrained(
            SD_MODEL_ID,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            safety_checker=None
        )
        device = "cuda" if torch.cuda.is_available() else "cpu"
        _pipe = _pipe.to(device)
        # Optimize
        if device == "cpu":
            _pipe.enable_attention_slicing()
        print(f"[ImageGen] Loaded on {device}")
        return _pipe
    except Exception as e:
        print(f"[ImageGen] Failed to load SD pipeline: {e}")
        return None

def _sanitize_filename(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9_\- ]", "", text)
    text = text.strip().replace(" ", "_")[:40]
    return text or "panel"

def _generate_placeholder(prompt: str, save_path: str, panel_number: int, art_style: str):
    """Create a nice comic placeholder image using Pillow"""
    W, H = 512, 512
    # Color palette based on art style
    palettes = {
        "anime": [(255, 183, 197), (255, 240, 245)],
        "comic book": [(255, 215, 0), (255, 69, 0)],
        "pixel art": [(0, 255, 136), (0, 100, 80)],
        "realistic": [(70, 130, 180), (25, 25, 112)],
        "cartoon": [(255, 255, 100), (255, 150, 0)]
    }
    colors = palettes.get(art_style.lower(), [(138, 43, 226), (75, 0, 130)])
    
    img = Image.new("RGB", (W, H), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Gradient background approximation
    for y in range(H):
        r = int(colors[0][0] + (colors[1][0]-colors[0][0]) * y / H)
        g = int(colors[0][1] + (colors[1][1]-colors[0][1]) * y / H)
        b = int(colors[0][2] + (colors[1][2]-colors[0][2]) * y / H)
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    
    # Panel border
    draw.rectangle([10, 10, W-10, H-10], outline=(0,0,0), width=6)
    draw.rectangle([18, 18, W-18, H-18], outline=(255,255,255), width=2)

    # Text
    try:
        font_big = ImageFont.truetype("arial.ttf", 28)
        font_small = ImageFont.truetype("arial.ttf", 16)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Center text
    title = f"PANEL {panel_number}"
    draw.text((W//2, H//2 - 40), title, fill=(255,255,255), font=font_big, anchor="mm", stroke_width=2, stroke_fill=(0,0,0))
    # Wrap prompt
    words = prompt.split()
    lines = []
    cur = ""
    for w in words:
        if len(cur + " " + w) < 35:
            cur = cur + " " + w if cur else w
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    preview = "\n".join(lines[:4])
    draw.text((W//2, H//2 + 30), preview, fill=(255,255,255), font=font_small, anchor="mm", align="center", stroke_width=1, stroke_fill=(0,0,0))
    draw.text((W//2, H-40), f"{art_style.upper()} STYLE", fill=(255,255,0), font=font_small, anchor="mm")

    img.save(save_path)
    return save_path

def generate_image(prompt: str, panel_number: int = 1, art_style: str = "comic book", setting: str = "") -> str:
    """
    Generates image from prompt and saves to static/panels.
    Returns relative path for web: static/panels/xxx.png
    """
    os.makedirs(STATIC_PANELS, exist_ok=True)
    safe = _sanitize_filename(prompt)
    filename = f"{panel_number}_{safe}_{uuid.uuid4().hex[:6]}.png"
    full_path = os.path.join(STATIC_PANELS, filename)
    rel_path = f"{STATIC_PANELS}/{filename}".replace("\\","/")

    # If mock or no GPU/low resource, use placeholder fast
    if MOCK_MODE:
        _generate_placeholder(prompt, full_path, panel_number, art_style)
        return rel_path

    pipe = _get_pipeline()
    if pipe is None:
        _generate_placeholder(prompt, full_path, panel_number, art_style)
        return rel_path

    try:
        enhanced = f"{prompt}, {art_style} style, comic book panel, dramatic, highly detailed, vibrant colors, sharp focus"
        import torch
        with torch.inference_mode():
            image = pipe(enhanced, num_inference_steps=25, guidance_scale=7.5).images[0]
        image.save(full_path)
        print(f"[ImageGen] Saved {full_path}")
        return rel_path
    except Exception as e:
        print(f"[ImageGen] Generation failed: {e}, using placeholder")
        _generate_placeholder(prompt, full_path, panel_number, art_style)
        return rel_path
