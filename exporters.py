import os
import datetime
from typing import List, Dict
from fpdf import FPDF
from ..config import STATIC_EXPORTS

class ComicPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "ComicCraft - AI Generated Comic", align="C", ln=True)
        self.ln(2)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def _clean(text: str) -> str:
    return text.encode('latin-1', 'replace').decode('latin-1')

def save_pdf(layout: List[Dict], character: str, prompt: str) -> str:
    """
    Compiles comic into PDF. Returns path to PDF.
    """
    os.makedirs(STATIC_EXPORTS, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_char = "".join([c for c in character if c.isalnum()])[:15] or "hero"
    filename = f"comic_{safe_char}_{timestamp}.pdf"
    full_path = os.path.join(STATIC_EXPORTS, filename)
    
    pdf = ComicPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    
    # Cover page
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.ln(30)
    pdf.multi_cell(0, 15, _clean(f"The Adventures of\n{character}"), align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 12)
    pdf.multi_cell(0, 8, _clean(f"Prompt: {prompt}"), align="C")
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 10)
    pdf.cell(0, 10, f"Generated on {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C", ln=True)

    # Panels
    for panel in layout:
        pdf.add_page()
        # Title
        pdf.set_font("Helvetica", "B", 14)
        pdf.cell(0, 10, _clean(f"Panel {panel['panel_number']}: {panel['title']}"), ln=True)
        pdf.ln(2)
        
        # Image
        img_path = panel.get("image_path", "")
        if img_path and os.path.exists(img_path):
            try:
                # Keep aspect ratio, max width
                pdf.image(img_path, x=10, w=190)
                pdf.ln(5)
            except Exception as e:
                print(f"PDF image error {img_path}: {e}")
                pdf.set_font("Helvetica", "I", 10)
                pdf.cell(0, 8, "[Image not available]", ln=True)
        else:
            pdf.set_font("Helvetica", "I", 10)
            pdf.cell(0, 8, "[Image placeholder]", ln=True)

        # Scene description italic
        pdf.set_font("Helvetica", "I", 11)
        pdf.multi_cell(0, 7, _clean(panel.get("scene_description","")))
        pdf.ln(3)

        # Caption
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(0, 7, _clean(f"Caption: {panel.get('caption','')}"))
        pdf.ln(2)

        # Narration
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, _clean(panel.get("narration","")))

        # Image prompt small
        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(100,100,100)
        pdf.multi_cell(0, 5, _clean(f"Art Prompt: {panel.get('image_prompt','')}"))
        pdf.set_text_color(0,0,0)

    pdf.output(full_path)
    print(f"[Exporter] PDF saved {full_path}")
    # Return path relative to static for download, and full path
    return full_path
