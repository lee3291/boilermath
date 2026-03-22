from processor import crop_and_upload
from database import engine, Problem, Exam, Tag, ProblemTag
from classifier import classify_problem, classify_page
from sqlalchemy.orm import Session
from sqlalchemy import select
from PIL import Image
import json
from storage import upload_image


# reprocess incorrectly cropped or tagged problems
def reprocess_problem(image_path, problem_number, exam_name):

    # re-call Gemini
    response = classify_page(image_path)
    result = json.loads(response)

    if not result["valid"]:
        print("No problems found on page")
        return

    # find the matching problem in Gemini's response
    matched = next(
        (p for p in result["problems"] if p["number"] == problem_number), None
    )
    if not matched:
        print(f"Problem {problem_number} not found in Gemini response")
        return

    # rebuild exam_dict
    parts = exam_name.split("-")
    exam_dict = {
        "name": exam_name,
        "number": parts[0][5:],
        "semester": parts[1],
        "problems_dir": f"output/MA{parts[0][:5]}/{exam_name}/problems",
        "s3_prefix": f"MA{parts[0][:5]}/{exam_name}",
    }

    im = Image.open(image_path)
    new_url = crop_and_upload(im, matched, exam_dict)

    # update DB
    with Session(engine) as session:
        problem = session.scalars(
            select(Problem)
            .join(Exam)
            .where(Exam.exam_number == exam_dict["number"])
            .where(Exam.semester == exam_dict["semester"])
            .where(Problem.problem_number == problem_number)
        ).first()

        if not problem:
            print(f"Problem {problem_number} not found in DB")
            return

        old_tags = session.scalars(
            select(ProblemTag).where(ProblemTag.problem_id == problem.id)
        ).all()

        for old_tag in old_tags:
            session.delete(old_tag)
        session.commit()

        # get or create the tag
        for tag_name in matched["tags"]:

            tag = session.scalars(select(Tag).where(Tag.name == tag_name)).first()

            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.commit()

            problem_tag = ProblemTag(problem_id=problem.id, tag_id=tag.id)
            session.add(problem_tag)

        problem.image_url = new_url
        problem.flagged = False
        session.commit()
        print(f"Reprocessed problem {problem_number} successfully")


def upload_manual_crop(image_path, problem_number, exam_name):
    parts = exam_name.split("-")
    exam_dict = {
        "name": exam_name,
        "number": parts[0][5:],
        "semester": parts[1],
        "problems_dir": f"output/MA{parts[0][:5]}/{exam_name}/problems",
        "s3_prefix": f"MA{parts[0][:5]}/{exam_name}",
    }

    key = f"{exam_dict['s3_prefix']}/problem-{problem_number}.png"

    response = classify_problem(image_path)
    result = json.loads(response)
    new_url = upload_image(image_path, key)

    # update DB
    with Session(engine) as session:
        problem = session.scalars(
            select(Problem)
            .join(Exam)
            .where(Exam.exam_number == exam_dict["number"])
            .where(Exam.semester == exam_dict["semester"])
            .where(Problem.problem_number == problem_number)
        ).first()

        if not problem:
            print(f"Problem {problem_number} not found in DB")
            return

        old_tags = session.scalars(
            select(ProblemTag).where(ProblemTag.problem_id == problem.id)
        ).all()

        for old_tag in old_tags:
            session.delete(old_tag)
        session.commit()

        # get or create the tag
        for tag_name in result["tags"]:

            tag = session.scalars(select(Tag).where(Tag.name == tag_name)).first()

            if not tag:
                tag = Tag(name=tag_name)
                session.add(tag)
                session.commit()

            problem_tag = ProblemTag(problem_id=problem.id, tag_id=tag.id)
            session.add(problem_tag)

        problem.image_url = new_url
        problem.flagged = False
        session.commit()
        print(f"Reprocessed problem {problem_number} successfully")


if __name__ == "__main__":
    image_path = "output/MA16200/16200E1-F2002/pages/page-4.png"
    problem_number = 7
    exam_name = "16200E1-F2002"
    reprocess_problem(image_path, problem_number, exam_name)
