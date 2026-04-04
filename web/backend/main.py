from fastapi import FastAPI
from backend.routers import problems, courses

app = FastAPI()
app.include_router(problems.router)
app.include_router(courses.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}
