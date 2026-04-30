def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]

    chunks = []
    current = ""

    for paragraph in paragraphs:
        if len(current) + len(paragraph) <= chunk_size:
            current = f"{current}\n\n{paragraph}".strip()
        else:
            if current:
                chunks.append(current)
            if len(paragraph) <= chunk_size:
                current = paragraph
            else:
                for i in range(0, len(paragraph), chunk_size - overlap):
                    chunks.append(paragraph[i: i + chunk_size])
                current = ""

    if current:
        chunks.append(current)

    return chunks
