from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from app.services.parser import parse_pdf, parse_text
from app.services.chunker import chunk_text
from app.services.openrouter import embed
from app.services.vector_store import save_chunks, search

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/cv")
async def upload_cv(session_id: int = Form(...), file: UploadFile = File(...)):
    if file.content_type not in ("application/pdf", "text/plain"):
        raise HTTPException(status_code=400, detail="Only PDF or plain text files are accepted.")
    content = await file.read()
    text = parse_pdf(content) if file.content_type == "application/pdf" else parse_text(content)
    chunks = chunk_text(text)
    embeddings = await embed(chunks)
    save_chunks(session_id, "cv", chunks, embeddings)
    return {"chunks": len(chunks), "preview": text[:500]}


@router.post("/jd")
async def upload_jd(session_id: int = Form(...), text: str = Form(...)):
    chunks = chunk_text(text)
    embeddings = await embed(chunks)
    save_chunks(session_id, "job_description", chunks, embeddings)
    return {"chunks": len(chunks), "preview": text[:500]}


class SearchRequest(BaseModel):
    session_id: int
    doc_type: str
    query: str
    top_k: int = 3


@router.post("/search")
async def search_documents(req: SearchRequest):
    query_embedding = await embed([req.query])
    results = search(req.session_id, req.doc_type, query_embedding[0], req.top_k)
    return {"results": results}
