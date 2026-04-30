from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from app.database import engine, Base, SessionLocal
from app.services.vector_store import init_vector_db
from app.routers.chat import router as chat_router
from app.routers.interview import router as interview_router
from app.routers.documents import router as documents_router
from app.routers.session import router as session_router
import app.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    init_vector_db()
    yield


app = FastAPI(title="Interview Coach API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)
app.include_router(interview_router)
app.include_router(documents_router)
app.include_router(session_router)


@app.get("/health")
def health():
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "ok"
    except Exception as e:
        db_status = str(e)

    status = "ok" if db_status == "ok" else "degraded"
    return JSONResponse(
        status_code=200 if status == "ok" else 503,
        content={"status": status, "db": db_status},
    )
