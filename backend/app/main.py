from fastapi import FastAPI
from app.database import engine, Base

app = FastAPI(title="Interview Coach API")

Base.metadata.create_all(bind=engine)


@app.get("/health")
def health():
    return {"status": "ok"}
