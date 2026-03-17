import requests
from bs4 import BeautifulSoup
import json

url = "https://www.math.purdue.edu/academic/courses/oldexams.php?course=MA16200"
response = requests.get(url)

if response.status_code == 200:
    print("Success")
else:
    print(f"Request failed with status code: {response.status_code}")

soup = BeautifulSoup(response.content, "html.parser")

all_links = soup.find_all("a")

ma16200 = {}

start_str = "https://www.math.purdue.edu"

for link in all_links:
    if link.get("href") and "serve_file.php" in link.get("href"):
        pdfLink = link.get("href")
        pdfName = pdfLink.split("file=")[1]
        examName = pdfName.replace("Ans-", "").replace("Sol-", "").replace(".pdf", "")

        if examName not in ma16200:
            ma16200[examName] = {"exam": None, "answer": None, "solution": None}

        examObj = ma16200[examName]

        if "Ans" in pdfName:
            examObj["answer"] = start_str + pdfLink
        elif "Sol" in pdfName:
            examObj["solution"] = start_str + pdfLink
        else:
            examObj["exam"] = start_str + pdfLink

for examName, examObj in ma16200.items():
    if examObj["exam"] is not None:
        url = examObj["exam"]
        filepath = "pdfs/MA16200/" + examName + ".pdf"
        response = requests.get(url)
        with open(filepath, "wb") as f:
            f.write(response.content)
