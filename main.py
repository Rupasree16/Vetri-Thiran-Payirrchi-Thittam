from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from .routes import router
import os

app = FastAPI(
    title="ComicCraft - AI Comic Story Creator",
    description="Generate personalized comics using Gemini + Stable Diffusion",
    version="1.0.0"
)

# Mount static
os.makedirs("app/static/panels", exist_ok=True)
os.makedirs("app/static/exports", exist_ok=True)
app.mount("/app/static", StaticFiles(directory="app/static"), name="static")
app.mount("/static", StaticFiles(directory="app/static"), name="static_root")

app.include_router(router)

@app.get("/docs2")
def root_docs():
    return {"message": "Go to /docs for Swagger, / for app"}
