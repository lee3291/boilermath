import pymupdf
from PIL import Image
import numpy as np

doc = pymupdf.open("pdfs/MA16200/16200E1-S2019.pdf")

for i in range(1, doc.page_count):
    page = doc[i]
    pix = page.get_pixmap()
    pix.save(f"output/page-{page.number}.png")

im = Image.open("output/page-1.png")
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

problems = []

for i in range(len(meaningful_gaps) - 1):
    problem_start = meaningful_gaps[i][1]
    problem_end = meaningful_gaps[i + 1][0]
    problems.append((problem_start, problem_end))

# Capture the last problem
problems.append((meaningful_gaps[-1][1], height))

for i in range(len(problems)):
    top, bottom = problems[i]
    cropped_img = im.crop((0, top, width, bottom))
    cropped_img.save(f"output/problems/problem-{i + 1}.png")
