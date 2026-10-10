import json
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.current_user import get_current_user
from app.db.dependencies import get_db
from app.models.ai_insight import AIInsight
from app.models.analysis_result import AnalysisResult
from app.models.analysis_skill import AnalysisSkill
from app.models.job_description import JobDescription
from app.models.missing_skill import MissingSkill
from app.models.resume import Resume
from app.models.skill import Skill
from app.models.user import User


router = APIRouter(
    prefix="/analyses",
    tags=["Analyses"]
)


@router.get("")
def list_my_analyses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Only analyses of resumes that belong to the logged-in user,
    # newest first, at most 50.
    rows = (
        db.query(AnalysisResult, Resume.file_name, JobDescription.title)
        .join(Resume, AnalysisResult.resume_id == Resume.id)
        .join(JobDescription, AnalysisResult.jd_id == JobDescription.id)
        .filter(Resume.user_id == current_user.id)
        .order_by(AnalysisResult.created_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "analysis_id": str(analysis.id),
            "resume_id": str(analysis.resume_id),
            "resume_file_name": file_name,
            "job_title": job_title,
            "ats_score": analysis.ats_score,
            "status": analysis.status,
            "created_at": analysis.created_at
        }
        for analysis, file_name, job_title in rows
    ]

def _load_list(text: str) -> list[str]:
    try:
        return json.loads(text)
    except ValueError:
        return []


@router.get("/{analysis_id}")
def get_analysis(
    analysis_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    row = (
        db.query(AnalysisResult, Resume.file_name, JobDescription.title)
        .join(Resume, AnalysisResult.resume_id == Resume.id)
        .join(JobDescription, AnalysisResult.jd_id == JobDescription.id)
        .filter(
            AnalysisResult.id == analysis_id,
            Resume.user_id == current_user.id
        )
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Analysis not found"
        )

    analysis, file_name, job_title = row

    matched_skills = [
        name
        for (name,) in (
            db.query(Skill.name)
            .join(AnalysisSkill, AnalysisSkill.skill_id == Skill.id)
            .filter(AnalysisSkill.analysis_id == analysis.id)
            .order_by(Skill.name)
            .all()
        )
    ]

    missing_skills = [
        name
        for (name,) in (
            db.query(Skill.name)
            .join(MissingSkill, MissingSkill.skill_id == Skill.id)
            .filter(MissingSkill.analysis_id == analysis.id)
            .order_by(Skill.name)
            .all()
        )
    ]

    insight = db.get(AIInsight, analysis.id)

    insights = None
    if insight:
        insights = {
            "summary": insight.summary,
            "strengths": _load_list(insight.strengths),
            "weaknesses": _load_list(insight.weaknesses),
            "achievements": _load_list(insight.achievements),
            "recommendations": _load_list(insight.recommendations)
        }

    return {
        "analysis_id": str(analysis.id),
        "resume_id": str(analysis.resume_id),
        "resume_file_name": file_name,
        "job_title": job_title,
        "ats_score": analysis.ats_score,
        "status": analysis.status,
        "created_at": analysis.created_at,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "insights": insights
    }