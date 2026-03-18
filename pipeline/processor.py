import pymupdf
import os
import shutil

course = "MA16200"

# Clean directory before running.
# shutil.rmtree(f"output/{course}", ignore_errors=True)

for exam_name in os.listdir(f"pdfs/{course}/"):
    exam_path = f"pdfs/{course}/{exam_name}"
    doc = pymupdf.open(exam_path)
    os.makedirs(f"output/{course}/{exam_name}/pages", exist_ok=True)

    # skip first page of PDF.
    for i in range(1, doc.page_count):
        page = doc[i]
        pix = page.get_pixmap()
        image_path = f"output/{course}/{exam_name}/pages/page-{i}.png"
        pix.save(image_path)
