from google import genai
from google.genai import types
from dotenv import load_dotenv
import os

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MA162_TAGS = [
    "vectors in the plane",
    "vectors in three dimensions",
    "dot product",
    "cross product",
    "regions between curves",
    "volumes by slicing",
    "volumes by shells",
    "arc length",
    "surface area",
    "physical applications of integrals",
    "work",
    "hydrostatic force",
    "center of mass",
    "integration by parts",
    "trigonometric integrals",
    "trigonometric substitution",
    "partial fraction decomposition",
    "improper integrals",
    "sequences",
    "series",
    "divergence test",
    "integral test",
    "comparison test",
    "limit comparison test",
    "alternating series test",
    "ratio test",
    "root test",
    "Taylor polynomials",
    "Taylor series",
    "Maclaurin series",
    "radius of convergence",
    "interval of convergence",
    "term-by-term differentiation",
    "term-by-term integration",
    "polar coordinates",
    "polar curves",
    "area in polar coordinates",
    "arc length in polar coordinates",
    "parametric equations",
    "parametric curves",
]


def classify_page(image_path):

    with open(image_path, "rb") as f:
        image_data = f.read()

    prompt = """
    You are a math exam processor. You will be given an image of a page from a university math exam.

    If this page contains no math problems (e.g. it is a cover page, instructions page, or formula sheet), return exactly:
    {"valid": false}

    Otherwise, for each math problem on the page:
    - Identify the problem number
    - Identify the mathematical concepts as tags. You MUST only use tags from this list: {MA162_TAGS}. Use lowercase. Choose the most specific applicable tags.
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
    You are a math exam processor. You will be given an image of a problem from a university math exam.

    Identify the mathematical concepts as tags. You MUST only use tags from this list: {MA162_TAGS}. Use lowercase. Choose the most specific applicable tags.

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
