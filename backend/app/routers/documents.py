from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.services.parser import parse_pdf, parse_text

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/cv")
async def upload_cv(file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "text/plain"):
        raise HTTPException(status_code=400, detail="Only PDF or plain text files are accepted.")
    content = await file.read()
    text = parse_pdf(content) if file.content_type == "application/pdf" else parse_text(content)
    return {"characters": len(text), "preview": text[:500]}


@router.post("/jd")
async def upload_jd(text: str = Form(...)):
    return {"characters": len(text), "preview": text[:500]}
