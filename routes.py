from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.templating import Jinja2Templates
import os, json

from .core.gemini_flash import generate_outline
from .core.gemini_pro import generate_story
from .core.image_generator import generate_image
from .core.layout_builder import build_comic_layout
from .core.exporters import save_pdf
from .models import PromptRequest, TestImageRequest
from .config import STATIC_EXPORTS

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Simple in-memory store for last comic (for PDF download & preview refresh)
last_comic_store = {
    "layout": None,
    "pdf_path": None,
    "meta": {}
}

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.post("/generate", response_class=HTMLResponse)
async def generate_comic_form(
    request: Request,
    prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...)
):
    try:
        # 1. Outline
        outline = generate_outline(prompt, character_name, setting, tone, art_style)
        # 2. Story
        story_text = generate_story(outline, character_name, setting, tone, art_style, prompt)
        # 3. Images
        image_paths = []
        for panel in outline:
            img_path = generate_image(
                prompt=panel.get("image_prompt", prompt),
                panel_number=panel.get("panel_number", 1),
                art_style=art_style,
                setting=setting
            )
            image_paths.append(img_path)

        # 4. Layout
        layout = build_comic_layout(outline, story_text, image_paths)

        # 5. PDF
        pdf_path = save_pdf(layout, character_name, prompt)

        # Store for export success page
        last_comic_store["layout"] = layout
        last_comic_store["pdf_path"] = pdf_path
        last_comic_store["meta"] = {"character": character_name, "prompt": prompt}

        return templates.TemplateResponse("comic_preview.html", {
            "request": request,
            "layout": layout,
            "pdf_path": pdf_path,
            "character": character_name,
            "prompt": prompt,
            "pdf_filename": os.path.basename(pdf_path)
        })
    except Exception as e:
        print(f"Generate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate-comic/json")
async def generate_comic_json(req: PromptRequest):
    try:
        outline = generate_outline(req.prompt, req.character_name, req.setting, req.tone, req.art_style)
        story_text = generate_story(outline, req.character_name, req.setting, req.tone, req.art_style, req.prompt)
        image_paths = []
        for panel in outline:
            img_path = generate_image(panel.get("image_prompt", req.prompt), panel.get("panel_number",1), req.art_style, req.setting)
            image_paths.append(img_path)
        layout = build_comic_layout(outline, story_text, image_paths)
        pdf_path = save_pdf(layout, req.character_name, req.prompt)
        last_comic_store["layout"] = layout
        last_comic_store["pdf_path"] = pdf_path

        # Convert layout to be JSON serializable with web paths
        return JSONResponse({
            "outline": outline,
            "story_text": story_text,
            "layout": layout,
            "pdf_path": pdf_path,
            "pdf_download_url": f"/download-pdf/{os.path.basename(pdf_path)}"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/test-image")
async def test_image(req: TestImageRequest):
    try:
        path = generate_image(req.prompt, panel_number=1, art_style=req.art_style)
        return {"image_path": path, "web_path": "/" + path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    pdf_path = last_comic_store.get("pdf_path") or ""
    return templates.TemplateResponse("export_success.html", {
        "request": request,
        "pdf_path": pdf_path,
        "pdf_filename": os.path.basename(pdf_path) if pdf_path else ""
    })

@router.get("/download-pdf/{filename}")
async def download_pdf(filename: str):
    full_path = os.path.join(STATIC_EXPORTS, filename)
    if not os.path.exists(full_path):
        raise HTTPException(status_code=404, detail="PDF not found")
    return FileResponse(full_path, media_type="application/pdf", filename=filename)

@router.get("/health")
async def health():
    return {"status": "ok", "mock_mode": os.getenv("MOCK_MODE")}
