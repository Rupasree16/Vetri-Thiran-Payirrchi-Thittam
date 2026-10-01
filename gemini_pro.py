import re
import random
from typing import List, Dict
from ..config import GOOGLE_API_KEY, MOCK_MODE, GEMINI_PRO_MODEL

MOCK_STORIES = [
    "CAPTION: The forest hums with ancient magic.\nNARRATION: {character} tightens their grip, eyes sparkling with determination. 'This is where it all begins,' they whisper.",
    "CAPTION: Sunlight dances through the leaves.\nNARRATION: '{character} steps forward, heart pounding. The forest feels alive, watching every move.",
    "CAPTION: A soft glow appears ahead.\nNARRATION: 'Who are you?' asks {character}. The creature giggles, 'A guide... or a trickster. Solve this: I speak without a mouth...'",
    "CAPTION: The ground cracks! A test of bravery.\nNARRATION: {character} leaps! 'I won't fall! Not today!' Wind rushes past as they soar.",
    "CAPTION: Golden light floods the exit.\nNARRATION: {character} smiles, the enchanted forest behind them. 'Adventure never ends — it just changes form.' THE END."
]

def _mock_story(outline: List[Dict], character: str, setting: str, tone: str) -> str:
    # Build a formatted text that layout_builder can parse
    panels_text = []
    for i, panel in enumerate(outline):
        story_line = MOCK_STORIES[i % len(MOCK_STORIES)].format(character=character)
        panels_text.append(f"Panel {panel['panel_number']}: {panel['title']}\n{story_line}\n")
    return "\n".join(panels_text)

def generate_story(outline: List[Dict], character: str, setting: str, tone: str, art_style: str, prompt: str) -> str:
    """
    Uses Gemini Pro to expand outline into narration + dialogues.
    Returns a single formatted text with Panel markers.
    """
    if MOCK_MODE:
        return _mock_story(outline, character, setting, tone)

    try:
        import google.generativeai as genai
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel(GEMINI_PRO_MODEL)

        outline_str = "\n".join([f"Panel {p['panel_number']}: {p['title']} - {p['scene_description']} (Image: {p['image_prompt']})" for p in outline])

        system_prompt = f"""
You are a master comic book writer. Expand the following 5-panel outline into full comic narration.

Story Prompt: {prompt}
Main Character: {character}
Setting: {setting}
Tone: {tone}
Art Style: {art_style}

Outline:
{outline_str}

For EACH panel, output exactly in this format:
Panel X: <Title>
CAPTION: <ambient description, background sound, 1 sentence>
NARRATION: <character action, emotion, dialogue in quotes, 2-3 sentences, engaging, matches {tone} tone>

Keep panels sequential. Keep {character} as hero. Make it cohesive, visual, comic-style. No extra explanation.
"""
        response = model.generate_content(system_prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[Gemini Pro] Error: {e}, fallback to mock")
        return _mock_story(outline, character, setting, tone)

def parse_story_to_panels(story_text: str) -> Dict[int, Dict[str, str]]:
    """
    Parses story text into dict panel_number -> {caption, narration, raw}
    """
    panels = {}
    # Split by Panel marker
    pattern = r"Panel\s*(\d+)\s*:\s*(.*)"
    matches = list(re.finditer(pattern, story_text, re.IGNORECASE))
    for idx, match in enumerate(matches):
        num = int(match.group(1))
        start = match.end()
        end = matches[idx+1].start() if idx+1 < len(matches) else len(story_text)
        block = story_text[start:end].strip()
        caption = ""
        narration = ""
        cap_match = re.search(r"CAPTION\s*:\s*(.*)", block, re.IGNORECASE)
        narr_match = re.search(r"NARRATION\s*:\s*(.*)", block, re.IGNORECASE | re.DOTALL)
        if cap_match:
            caption = cap_match.group(1).strip().split("\n")[0]
        if narr_match:
            narration = narr_match.group(1).strip()
        else:
            narration = block
        panels[num] = {"caption": caption, "narration": narration, "raw": block}
    return panels
