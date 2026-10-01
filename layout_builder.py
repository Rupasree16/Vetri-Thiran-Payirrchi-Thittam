from typing import List, Dict
from .gemini_pro import parse_story_to_panels

def build_comic_layout(outline: List[Dict], story_text: str, image_paths: List[str]) -> List[Dict]:
    """
    Organizes images + story + outline into structured layout.
    Returns list of panels with all data needed for frontend and PDF.
    """
    parsed = parse_story_to_panels(story_text)
    
    layout = []
    for i, out in enumerate(outline):
        panel_num = out.get("panel_number", i+1)
        title = out.get("title", f"Panel {panel_num}")
        scene_desc = out.get("scene_description", "")
        image_prompt = out.get("image_prompt", "")
        image_path = image_paths[i] if i < len(image_paths) else ""

        story_data = parsed.get(panel_num, {})
        caption = story_data.get("caption", f"Scene {panel_num}")
        narration = story_data.get("narration", story_data.get("raw", "No narration generated."))
        
        layout.append({
            "panel_number": panel_num,
            "title": title,
            "scene_description": scene_desc,
            "image_prompt": image_prompt,
            "image_path": image_path,  # e.g. app/static/panels/xxx.png
            "web_image_path": "/" + image_path if not image_path.startswith("/") else image_path,  # for <img src>
            "caption": caption,
            "narration": narration
        })
    return layout
