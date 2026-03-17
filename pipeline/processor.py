import pymupdf

doc = pymupdf.open("pdfs/MA16200/16200E1-S2019.pdf")


for i in range(doc.page_count):
    page = doc[i]
    pix = page.get_pixmap()
    pix.save(f"output/page-{page.number}.png")
