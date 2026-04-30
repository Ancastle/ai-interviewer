from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routers.chat import router as chat_router
import app.models


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Interview Coach API", lifespan=lifespan)
app.include_router(chat_router)


@app.get("/health")
def health():
    return {"status": "ok"}
