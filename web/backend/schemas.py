from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class Tag(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class Exam(BaseModel):
    id: int
    course: str
    semester: str
    exam_number: str
    model_config = ConfigDict(from_attributes=True)


class Problem(BaseModel):
    id: int
    problem_number: int
    exam: Exam
    tags: List[Tag]
    model_config = ConfigDict(from_attributes=True)


class ProblemDetail(Problem):
    image_url: str
    answer: Optional[str] = None
    solution_url: Optional[str] = None
    flagged: bool
    model_config = ConfigDict(from_attributes=True)
