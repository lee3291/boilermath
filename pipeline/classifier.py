from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def classify_page(image_path):

    with open(image_path, "rb") as f:
        image_data = f.read()

    prompt = """
    You are a math exam processor. You will be given an image of a page from a university math exam.

    If this page contains no math problems (e.g. it is a cover page, instructions page, or formula sheet), return exactly:
    {"valid": false}

    Otherwise, for each math problem on the page:
    - Identify the problem number
    - Identify the mathematical concepts as tags (e.g. "vectors", "integration by parts", "Taylor series")
    - Provide a bounding box with top and bottom y-values normalized to 0-1000 (0 = top of image, 1000 = bottom)
    - The bounding box MUST include the full problem statement, all sub-parts, all answer choices, and any figures or diagrams
    - Be GENEROUS with the bounding box — extend it slightly beyond what you think is needed to avoid cutting off content
    - Problems end where the next large whitespace gap begins

    Return JSON only, no markdown, no explanation:
    {
    "valid": true,
    "problems": [
        {
        "number": 1,
        "tags": ["concept1", "concept2"],
        "top": 120,
        "bottom": 380
        }
    ]
    }"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_data, mime_type="image/png"),
            prompt,
        ],
    )

    return (
        response.text.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )


def classify_problem(image_path):
    with open(image_path, "rb") as f:
        image_data = f.read()

    prompt = """
    You are a math exam processor. You will be given an image of a single math problem from a university exam.

    Identify the mathematical concepts as tags (e.g. "vectors", "integration by parts", "Taylor series").

    Return JSON only, no markdown, no explanation:
    {
        "tags": ["concept1", "concept2"]
    }"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Part.from_bytes(data=image_data, mime_type="image/png"),
            prompt,
        ],
    )

    return (
        response.text.strip()
        .removeprefix("```json")
        .removeprefix("```")
        .removesuffix("```")
        .strip()
    )
