import json
import re
import random
from typing import List, Dict
from ..config import GOOGLE_API_KEY, MOCK_MODE, GEMINI_FLASH_MODEL

# Mock outlines for offline testing
MOCK_OUTLINES = [
    [
        {"panel_number": 1, "title": "The Call to Adventure", "scene_description": "Our hero stands at the edge of the enchanted forest, morning mist swirling.", "image_prompt": "brave hero at edge of enchanted forest, morning mist, comic book style, dramatic lighting"},
        {"panel_number": 2, "title": "Into the Deep Woods", "scene_description": "The trees whisper as the hero steps in, light beams cutting through canopy.", "image_prompt": "hero walking into deep magical forest, sunbeams through trees, comic style"},
        {"panel_number": 3, "title": "The Mysterious Encounter", "scene_description": "A glowing creature appears, offering a cryptic riddle.", "image_prompt": "glowing magical creature meeting hero in forest clearing, fantasy comic"},
        {"panel_number": 4, "title": "The Trial", "scene_description": "A sudden chasm opens, testing courage and wit.", "image_prompt": "hero leaping over chasm in forest, action pose, comic book art"},
        {"panel_number": 5, "title": "Triumph and Return", "scene_description": "Hero emerges victorious, forest cheering with rustling leaves.", "image_prompt": "hero triumphant at forest exit, golden sunset, epic comic finale"}
    ]
]

def generate_outline(prompt: str, character: str, setting: str, tone: str, art_style: str) -> List[Dict]:
    """
    Uses Gemini Flash to generate a structured 5-panel outline.
    Returns list of dicts: panel_number, title, scene_description, image_prompt
    """
    if MOCK_MODE:
        base = random.choice(MOCK_OUTLINES)
        # Customize with user inputs
        outline = []
        for p in base:
            outline.append({
                "panel_number": p["panel_number"],
                "title": f"{p['title']} - {character} in {setting}",
                "scene_description": f"{p['scene_description']} Tone: {tone}. Story: {prompt[:120]}",
                "image_prompt": f"{p['image_prompt']}, main character named {character}, setting {setting}, {art_style} art style, {tone} mood, highly detailed comic panel, 4k"
            })
        return outline

    # Real Gemini call
    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(GEMINI_FLASH_MODEL)

        system_prompt = f"""
You are a comic book outline generator. Create a structured 5-panel comic outline.
User Story Prompt: {prompt}
Main Character: {character}
Setting: {setting}
Tone: {tone}
Art Style: {art_style}

Output STRICT JSON array of 5 objects, each with:
- panel_number (1-5)
- title (short, catchy, 3-6 words)
- scene_description (1-2 sentences setting the scene)
- image_prompt (detailed Stable Diffusion prompt: character {character} in {setting}, {art_style} style, {tone} tone, comic book panel, vivid colors, dynamic)

Example:
[
  {{"panel_number":1, "title":"The Beginning", "scene_description":"...", "image_prompt":"..."}},
  ...
]
Return ONLY JSON array, no markdown.
"""
        response = model.generate_content(system_prompt)
        text = response.text.strip()
        # Clean markdown fences
        text = re.sub(r"```json|```", "", text).strip()
        outline = json.loads(text)
        # Validate
        if isinstance(outline, list) and len(outline) >= 5:
            return outline[:5]
        else:
            raise ValueError("Invalid outline format")
    except Exception as e:
        print(f"[Gemini Flash] Error: {e}, falling back to mock")
        # Fallback mock
        return generate_outline(prompt, character, setting, tone, art_style) if False else MOCK_OUTLINES[0]
