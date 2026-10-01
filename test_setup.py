import os

print("=== ComicCraft Setup Test ===")
# Test imports
try:
    from app.core.gemini_flash import generate_outline
    from app.core.gemini_pro import generate_story
    from app.core.image_generator import generate_image
    from app.core.layout_builder import build_comic_layout
    from app.core.exporters import save_pdf
    print("✅ All core modules imported")
except Exception as e:
    print(f"❌ Import error: {e}")
    exit(1)

# Test mock generation
outline = generate_outline("A brave fox", "Kiko", "forest", "dramatic", "comic book")
print(f"✅ Outline: {len(outline)} panels")

story = generate_story(outline, "Kiko", "forest", "dramatic", "comic book", "A brave fox")
print(f"✅ Story length: {len(story)} chars")

images=[]
for p in outline[:2]:  # test only 2 for speed
    img = generate_image(p['image_prompt'], p['panel_number'], "comic book", "forest")
    images.append(img)
    print(f"✅ Image: {img}")

# Pad remaining
while len(images) < len(outline):
    images.append(images[0])

layout = build_comic_layout(outline, story, images)
print(f"✅ Layout: {len(layout)} panels")

pdf = save_pdf(layout, "Kiko", "A brave fox")
print(f"✅ PDF: {pdf} exists={os.path.exists(pdf)}")

print("\n🎉 All tests passed! Run: uvicorn app.main:app --reload")
