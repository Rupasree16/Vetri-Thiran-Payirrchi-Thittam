# ComicCraft - AI Comic Story Creator using Gemini Models

A web-based application that uses AI to generate personalized comic book stories and illustrations.

## Architecture
- **Frontend**: HTML + CSS + Jinja2
- **Backend**: FastAPI
- **AI**: 
  - Gemini 1.5 Flash → structured 5-panel outline
  - Gemini 1.5 Pro → narration & dialogues
  - Stable Diffusion (runwayml/stable-diffusion-v1-5) → comic illustrations
- **Export**: FPDF2 for PDF generation

## Project Structure
```
ComicCraft/
├── app/
│   ├── main.py              # FastAPI app
│   ├── routes.py            # All routes: /, /generate, /generate-comic/json, /test-image, /export-success, /download-pdf
│   ├── config.py            # Env + model config
│   ├── models.py            # Pydantic schemas
│   ├── core/
│   │   ├── gemini_flash.py  # generate_outline()
│   │   ├── gemini_pro.py    # generate_story() + parse_story_to_panels()
│   │   ├── image_generator.py # generate_image() with placeholder fallback
│   │   ├── layout_builder.py  # build_comic_layout()
│   │   └── exporters.py     # save_pdf()
│   ├── templates/
│   │   ├── index.html
│   │   ├── comic_preview.html
│   │   └── export_success.html
│   └── static/
│       ├── panels/          # Generated images
│       └── exports/          # Generated PDFs
├── requirements.txt
├── .env.example
├── test_setup.py
└── README.md
```

## API Endpoints
- `GET /` → Homepage form
- `POST /generate` → Form-based comic generation → renders comic_preview.html
- `POST /generate-comic/json` → JSON API → returns layout + PDF path
- `POST /test-image` → Test image generation alone
- `GET /export-success` → Success page
- `GET /download-pdf/{filename}` → Download PDF
- `GET /docs` → Swagger docs

## Quick Start (VS Code)

### 1. Prerequisites
- Python 3.10+
- VS Code
- (Optional) Gemini API Key from https://aistudio.google.com/app/apikey

### 2. Setup in VS Code
```bash
# Clone / unzip project
cd ComicCraft

# Create venv
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# Note: torch CPU is used by default for low resource. For GPU, install torch separately.

# Env
cp .env.example .env
# Edit .env and put GOOGLE_API_KEY=your_key
# If no key, app runs in MOCK_MODE with placeholder images and stories
```

### 3. Run
```bash
uvicorn app.main:app --reload --port 8000
```
Open http://127.0.0.1:8000
Swagger: http://127.0.0.1:8000/docs

### 4. Test
```bash
python test_setup.py
```
This tests full pipeline in mock mode: outline → story → 2 images → layout → PDF

### 5. Use
1. Fill form: prompt, character, setting, tone, art style
2. Click Generate (30-60s if SD loads, 2-3s in mock)
3. View 5-panel comic preview
4. Download PDF
5. Export success page

## Mock Mode vs Real AI
- If GOOGLE_API_KEY missing or MOCK_MODE=true → Uses crafted mock stories + Pillow placeholder images (no internet/GPU needed)
- If key present → Calls Gemini Flash/Pro. If Stable Diffusion fails to load, still uses Pillow fallback so app never crashes.

## Troubleshooting
- **Torch / Diffusers heavy**: App lazy-loads SD only when needed. If low RAM, keep MOCK_MODE=true.
- **PDF images missing**: Check app/static/panels exists.
- **Gemini quota**: Enable mock or wait.
- **Port in use**: `uvicorn app.main:app --port 8001`

## Future Enhancements
- User accounts & comic library
- Multi-page arcs
- Edit panels
- Shareable links

Made with ❤️ for storytelling democratization.
