from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from typing import Optional, List


class Base(DeclarativeBase):
    pass


class Exam(Base):
    __tablename__ = "exam"
    id: Mapped[int] = mapped_column(primary_key=True)
    course: Mapped[str] = mapped_column(String(7))
    semester: Mapped[str] = mapped_column(String(5))
    exam_number: Mapped[str] = mapped_column(String(5))
    problems: Mapped[List["Problem"]] = relationship()


class Problem(Base):
    __tablename__ = "problem"
    id: Mapped[int] = mapped_column(primary_key=True)
    exam_id: Mapped[int] = mapped_column(ForeignKey("exam.id"))
    problem_number: Mapped[int] = mapped_column()
    image_url: Mapped[str] = mapped_column()
    answer: Mapped[Optional[str]] = (
        mapped_column()
    )  # optional for now but should not be nullible or optional eventually.
    solution_url: Mapped[Optional[str]] = mapped_column()
    flagged: Mapped[bool] = mapped_column(default=False, server_default="false")
    exam: Mapped["Exam"] = relationship()
    tags: Mapped[List["Tag"]] = relationship(secondary="problem_tag")


class Tag(Base):
    __tablename__ = "tag"
    __table_args__ = (UniqueConstraint("name", "course"),)
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    course: Mapped[str] = mapped_column(String(7))


class ProblemTag(Base):
    __tablename__ = "problem_tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problem.id"))
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id"))
