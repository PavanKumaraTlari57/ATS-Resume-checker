from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.resume import router as resumes_router
from app.routers.analysis import router as analyses_router
app = FastAPI()
app.include_router(auth_router)
app.include_router(resumes_router)
app.include_router(analyses_router)

@app.get("/")
def read_root():
    return {"message": "Hello AI Resume Analyzer"}