from fastapi import APIRouter, Query
from sqlalchemy import select, func
from backend.database import SessionDep
from backend.models import Exam, Tag
from backend.models import Problem as ProblemModel
from backend.schemas import Problem as ProblemSchema
from typing import Optional, List

router = APIRouter()


@router.get("/courses/{course}/problems", response_model=List[ProblemSchema])
async def read_problems(
    course: str,
    session: SessionDep,
    skip: int = 0,
    limit: int = 50,
    tags: Optional[List[str]] = Query(default=None),
    exam: Optional[str] = None,
    year: Optional[str] = None,
    semester: Optional[str] = None,
):
    query = select(ProblemModel).join(Exam).where(Exam.course == course)

    # only match the problems that have exactly the same tags.
    if tags:
        query = (
            query.join(ProblemModel.tags)
            .where(Tag.name.in_(tags))
            .group_by(ProblemModel.id)
            .having(func.count(Tag.id) == len(tags))
        )

    if exam:
        query = query.where(Exam.exam_number == exam)

    if semester:
        query = query.where(Exam.semester.startswith(semester))

    if year:
        query = query.where(Exam.semester.endswith(year))

    problems = session.scalars(query.offset(skip).limit(limit)).all()
    return problems
