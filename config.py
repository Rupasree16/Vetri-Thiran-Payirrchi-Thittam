import os
try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

# If no key, auto mock
if not GOOGLE_API_KEY or GOOGLE_API_KEY == "your_gemini_api_key_here":
    MOCK_MODE = True

STATIC_PANELS = "app/static/panels"
STATIC_EXPORTS = "app/static/exports"

# Models
GEMINI_FLASH_MODEL = "models/gemini-1.5-flash"
GEMINI_PRO_MODEL = "models/gemini-1.5-pro"
SD_MODEL_ID = "runwayml/stable-diffusion-v1-5"
