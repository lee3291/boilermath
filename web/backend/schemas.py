from pydantic import BaseModel
from typing import List, Optional


class Tag(BaseModel):
    id: int
    name: str
    # should there be course? I mean the problem and the exam info will have the course. identifiying the tag is enough with the id.


class ExamInfo(BaseModel):
    id: int
    course: str
    semester: str
    exam_number: str


class Problem(BaseModel):
    id: int
    problem_number: int
    exam_info: ExamInfo
    tags: List[Tag]


class ProblemDetail(Problem):
    image_url: str
    answer: Optional[str] = None
    solution_url: Optional[str] = None
    flagged: bool
