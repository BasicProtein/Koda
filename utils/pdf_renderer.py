from typing import List
import fitz  # PyMuPDF


def render_pdf_pages(pdf_path, dpi: int = 150) -> List[bytes]:
    doc = fitz.open(pdf_path)
    images = []
    for page in doc:
        mat = fitz.Matrix(dpi / 72.0, dpi / 72.0)
        pix = page.get_pixmap(matrix=mat)
        images.append(pix.tobytes('png'))
    return images
