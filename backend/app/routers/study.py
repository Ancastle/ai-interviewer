from fastapi import APIRouter
from app.services.study_reader import get_subjects, get_categories

router = APIRouter(prefix="/study", tags=["study"])


@router.get("/subjects")
def list_subjects():
    return {"subjects": get_subjects()}


@router.get("/{subject}/categories")
def list_categories(subject: str):
    return {"categories": get_categories(subject)}
