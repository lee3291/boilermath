import pymupdf
from PIL import Image
import numpy as np
import os
import shutil

course = "MA16200"

# Clean directory before running.
shutil.rmtree(f"output/{course}", ignore_errors=True)

for exam_name in os.listdir(f"pdfs/{course}/"):
    exam_path = f"pdfs/{course}/{exam_name}"
    doc = pymupdf.open(exam_path)
    os.makedirs(f"output/{course}/{exam_name}/pages", exist_ok=True)
    os.makedirs(f"output/{course}/{exam_name}/problems", exist_ok=True)

    problem_count = 1
    # skip first page of PDF.
    for i in range(1, doc.page_count):
        page = doc[i]
        pix = page.get_pixmap()
        image_path = f"output/{course}/{exam_name}/pages/page-{i}.png"
        pix.save(image_path)

        im = Image.open(image_path)
        grayscale_im = im.convert("L")
        img_array = np.array(grayscale_im)
        height, width = img_array.shape[:2]

        in_gap = False
        gap_start = 0
        gaps = []
        for y in range(height):
            row_pixels = img_array[y]
            if np.all(row_pixels > 250) and not in_gap:
                gap_start = y
                in_gap = True
            if not np.all(row_pixels > 250) and in_gap:
                gaps.append((gap_start, y))
                in_gap = False

        min_gap = 30
        meaningful_gaps = [(start, end) for start, end in gaps if end - start > min_gap]

        if len(meaningful_gaps) == 0:
            print(f"No gaps found: {exam_name}, page {i}")
            continue

        problems = []

        for j in range(len(meaningful_gaps) - 1):
            problem_start = meaningful_gaps[j][1]
            problem_end = meaningful_gaps[j + 1][0]
            problems.append((problem_start, problem_end))

        # Capture the last problem
        problems.append((meaningful_gaps[-1][1], height))

        for k in range(len(problems)):
            top, bottom = problems[k]
            cropped_img = im.crop((0, top, width, bottom))
            cropped_img.save(
                f"output/{course}/{exam_name}/problems/problem-{problem_count}.png"
            )
            problem_count += 1
