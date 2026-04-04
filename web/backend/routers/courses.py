from fastapi import APIRouter
from sqlalchemy import select, distinct
from backend.database import SessionDep
from backend.models import Exam

router = APIRouter()


@router.get("/course/")
async def read_courses(session: SessionDep):
    result = session.execute(select(distinct(Exam.course)))
    return result.scalars().all()
