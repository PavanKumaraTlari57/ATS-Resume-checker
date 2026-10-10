import uuid
from pathlib import Path
 
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
 
from app.core.current_user import get_current_user
from app.db.dependencies import get_db
from app.models.resume import Resume
from app.models.user import User
from app.services.pdf_parser import extract_text_from_pdf
from pydantic import BaseModel, Field
from app.services.ai_skills import analyze_skills
from app.services.analysis_storage import save_analysis, save_insights
from app.services.ai_insights import generate_insights
 
 
router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)
 
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
 
 
@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    original_name = file.filename or "resume.pdf"
 
    # Check 1: only PDF files
    if not original_name.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
 
    # Check 2: file must not be bigger than 5 MB
    content = file.file.read(MAX_FILE_SIZE + 1)
 
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File is too large (maximum 5 MB)"
        )
 
    # Check 3: a real PDF always starts with these bytes
    if not content.startswith(b"%PDF"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is not a valid PDF"
        )
 
    # Save the file with a random name so names never clash
    UPLOAD_DIR.mkdir(exist_ok=True)
    stored_path = UPLOAD_DIR / f"{uuid.uuid4()}.pdf"
    stored_path.write_bytes(content)
 
    # Save the details in the database
    resume = Resume(
        user_id=current_user.id,
        file_name=original_name[:100],
        file_size=len(content),
        file_type="pdf",
        storage_path=str(stored_path)
    )
 
    db.add(resume)
    db.commit()
    db.refresh(resume)
 
    return {
        "id": str(resume.id),
        "file_name": resume.file_name,
        "file_size": resume.file_size,
        "uploaded_at": resume.uploaded_at
    }

@router.get("/{resume_id}/text")
def get_resume_text(
    resume_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    text = extract_text_from_pdf(resume.storage_path)

    return {
        "resume_id": str(resume.id),
        "characters": len(text),
        "text": text
    }

class AnalyzeRequest(BaseModel):
    job_description: str = Field(min_length=20, max_length=10000)


@router.post("/{resume_id}/analyze")
def analyze_resume(
    resume_id: uuid.UUID,
    data: AnalyzeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Resume not found"
        )

    text = extract_text_from_pdf(resume.storage_path)

    if not text:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not read any text from this PDF"
        )

    try:
        result = analyze_skills(text, data.job_description)
    except Exception as error:
        print("AI error:", error)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="AI service failed, please try again"
        )

    try:
        insights = generate_insights(text, data.job_description, result)
    except Exception as error:
        print("AI insights error:", error)
        insights = None

    analysis = save_analysis(db, resume.id, data.job_description, result)

    if insights:
        save_insights(db, analysis.id, insights)

    return {
        "analysis_id": str(analysis.id),
        "resume_id": str(resume.id),
        **result,
        "insights": insights
    }