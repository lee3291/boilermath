import pymupdf
import os
import shutil
from classifier import classify_page
import time
import json
from PIL import Image
from storage import upload_image
from sqlalchemy.orm import Session
from database import engine, Exam, Problem, Tag, ProblemTag
from typing import List
from sqlalchemy import select
import numpy as np

COURSE = "MA16200"


# goes thorugh the pipeline to process each exam for all pdfs.
# file_name = "16200E1-F2002.png"
def process_exam(file_name):
    exam_name = file_name.replace(".pdf", "")  # "16200E1-F2002"
    parts = exam_name.split("-")  # ["16200E1", "F2002"]
    exam_number = parts[0][5:]  # "E1"
    semester = parts[1]  # "F2002"

    exam_dict = {
        "name": exam_name,
        "number": exam_number,
        "semester": semester,
        "pdf_path": f"pdfs/{COURSE}/{file_name}",
        "pages_dir": f"output/{COURSE}/{exam_name}/pages",
        "problems_dir": f"output/{COURSE}/{exam_name}/problems",
        "s3_prefix": f"{COURSE}/{exam_name}",
    }

    if exam_already_in_db(exam_dict):
        print(f"Skipping {exam_name}, already processed")
        return

    image_paths = generate_page_images(exam_dict)

    for image_path in image_paths:
        # Gemini API call, wait 12 sec for free plan limit
        response = classify_page(image_path)

        # debug print
        # print(response)
        # dp

        result = json.loads(response)
        if not result["valid"]:
            continue
        im = Image.open(image_path)

        # debug print
        # image_width, image_height = im.size
        # print(f"Image height: {image_height}")
        # dp

        for problem in result["problems"]:

            # debug print
            # print(f"Problem {problem['number']}: top={problem['top']}, bottom={problem['bottom']}")
            # dp

            s3_image_url = crop_and_upload(im, problem, exam_dict)
            write_to_db(exam_dict, problem, s3_image_url)


# checks if an exam has already been processed and is in DB.
def exam_already_in_db(exam_dict):
    with Session(engine) as session:
        exam = session.scalars(
            select(Exam)
            .where(Exam.course == COURSE)
            .where(Exam.semester == exam_dict["semester"])
            .where(Exam.exam_number == exam_dict["number"])
        ).first()
        return exam is not None


# creates a directory in output/exam_name/pages/ and creates image files of each page from pdf.
def generate_page_images(exam_dict) -> List[str]:
    os.makedirs(exam_dict["pages_dir"], exist_ok=True)
    # skip first page of PDF.
    doc = pymupdf.open(exam_dict["pdf_path"])
    image_paths = []
    for i in range(1, doc.page_count):
        page = doc[i]
        mat = pymupdf.Matrix(2, 2)
        pix = page.get_pixmap(matrix=mat)
        image_path = f"{exam_dict['pages_dir']}/page-{i}.png"
        pix.save(image_path)
        image_paths.append(image_path)
    return image_paths


# with the given problem object, crops the image, saves it as an image and uploads to S3
def crop_and_upload(im, problem, exam_dict):
    # get metadata
    image_width, image_height = im.size
    number = problem["number"]
    padding_top = 20
    padding_bottom = 80
    top = max(0, int(problem["top"] / 1000 * image_height) - padding_top)
    bottom = min(
        image_height, int(problem["bottom"] / 1000 * image_height) + padding_bottom
    )
    im_gray = np.array(im.convert("L"))
    bottom = find_true_bottom(im_gray, bottom, image_height=image_height)

    # crop problem image and save
    cropped = im.crop((0, top, image_width, bottom))
    problem_path = f"{exam_dict['problems_dir']}/problem-{number}.png"
    os.makedirs(exam_dict["problems_dir"], exist_ok=True)
    cropped.save(problem_path)

    # upload to S3 bucket
    key = f"{exam_dict['s3_prefix']}/problem-{number}.png"
    url = upload_image(problem_path, key)
    if url == "Failed":
        raise Exception(f"Failed to upload {problem_path} to S3")

    return url


# writes the problem to the DB and returns the url
def write_to_db(exam_dict, problem_obj, s3_image_url):

    with Session(engine) as session:
        # get or create exam
        exam = session.scalars(
            select(Exam)
            .where(Exam.course == COURSE)
            .where(Exam.semester == exam_dict["semester"])
            .where(Exam.exam_number == exam_dict["number"])
        ).first()

        if not exam:
            exam = Exam(
                course=COURSE,
                semester=exam_dict["semester"],
                exam_number=exam_dict["number"],
            )
            session.add(exam)
            session.commit()

        # write the problem
        problem = Problem(
            exam_id=exam.id,
            problem_number=problem_obj["number"],
            image_url=s3_image_url,
        )
        session.add(problem)
        session.commit()

        # get or create the tag
        for tag_name in problem_obj["tags"]:

            tag = session.scalars(
                select(Tag).where(Tag.name == tag_name).where(Tag.course == COURSE)
            ).first()

            if not tag:
                tag = Tag(name=tag_name, course=COURSE)
                session.add(tag)
                session.commit()

            problem_tag = ProblemTag(problem_id=problem.id, tag_id=tag.id)
            session.add(problem_tag)
            session.commit()


# find the true bottom of the problem from the image
def find_true_bottom(img_array, gemini_bottom, image_height):
    consecutive_white = 0
    for y in range(gemini_bottom, image_height):
        row = img_array[y]
        if np.all(row > 250):
            consecutive_white += 1
            if consecutive_white >= 20:
                return y - consecutive_white
        else:
            consecutive_white = 0
    return image_height


# Clean directory before running.
shutil.rmtree(f"output/{COURSE}", ignore_errors=True)

for file_name in os.listdir(f"pdfs/{COURSE}"):
    process_exam(file_name)
    break
