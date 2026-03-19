import requests
from bs4 import BeautifulSoup

# change course name for different courses.
course = "MA16200"

url = f"https://www.math.purdue.edu/academic/courses/oldexams.php?course={course}"
response = requests.get(url)

if response.status_code == 200:
    print("Success")
else:
    print(f"Request failed with status code: {response.status_code}")

soup = BeautifulSoup(response.content, "html.parser")

all_links = soup.find_all("a")

courseDict = {}

start_str = "https://www.math.purdue.edu"

for link in all_links:
    if link.get("href") and "serve_file.php" in link.get("href"):
        pdfLink = link.get("href")
        pdfName = pdfLink.split("file=")[1]
        examName = pdfName.replace("Ans-", "").replace("Sol-", "").replace(".pdf", "")

        if examName not in courseDict:
            courseDict[examName] = {"exam": None, "answer": None, "solution": None}

        examObj = courseDict[examName]

        if "Ans" in pdfName:
            examObj["answer"] = start_str + pdfLink
        elif "Sol" in pdfName:
            examObj["solution"] = start_str + pdfLink
        else:
            examObj["exam"] = start_str + pdfLink

for examName, examObj in courseDict.items():
    if examObj["exam"] is not None:
        url = examObj["exam"]
        filepath = f"pdfs/{course}/{examName}.pdf"
        response = requests.get(url)
        with open(filepath, "wb") as f:
            f.write(response.content)
