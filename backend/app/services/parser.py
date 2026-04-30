import io
from pypdf import PdfReader


def parse_pdf(content: bytes) -> str:
    reader = PdfReader(io.BytesIO(content))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n\n".join(pages).strip()


def parse_text(content: bytes) -> str:
    return content.decode("utf-8").strip()
