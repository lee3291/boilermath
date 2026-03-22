from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session
from typing import Optional
from dotenv import load_dotenv
import os

load_dotenv()

engine = create_engine(os.getenv("DATABASE_URL"))


class Base(DeclarativeBase):
    pass


class Exam(Base):
    __tablename__ = "exam"
    id: Mapped[int] = mapped_column(primary_key=True)
    course: Mapped[str] = mapped_column(String(7))
    semester: Mapped[str] = mapped_column(String(5))
    exam_number: Mapped[str] = mapped_column(String(5))


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


class Tag(Base):
    __tablename__ = "tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True)


class ProblemTag(Base):
    __tablename__ = "problem_tag"
    id: Mapped[int] = mapped_column(primary_key=True)
    problem_id: Mapped[int] = mapped_column(ForeignKey("problem.id"))
    tag_id: Mapped[int] = mapped_column(ForeignKey("tag.id"))


Base.metadata.drop_all(engine)
Base.metadata.create_all(engine)
