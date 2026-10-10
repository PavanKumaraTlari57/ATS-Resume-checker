import json
import uuid

from sqlalchemy.orm import Session

from app.models.analysis_result import AnalysisResult
from app.models.analysis_skill import AnalysisSkill
from app.models.job_description import JobDescription
from app.models.missing_skill import MissingSkill
from app.models.skill import Skill
from app.models.ai_insight import AIInsight


def _get_or_create_skill(db: Session, name: str) -> Skill:
    """Find a skill by name, or create it if it is new."""
    name = name.strip()[:100]

    skill = db.query(Skill).filter(Skill.name == name).first()

    if skill:
        return skill

    skill = Skill(name=name)
    db.add(skill)
    db.flush()  # sends it to the database so skill.id is available

    return skill


def save_analysis(
    db: Session,
    resume_id: uuid.UUID,
    job_description: str,
    result: dict
) -> AnalysisResult:
    """Save one finished analysis. Returns the saved AnalysisResult."""

    # The title column holds at most 50 characters, so we use the start
    # of the job description as a simple title.
    title = " ".join(job_description.split())[:50]

    job = JobDescription(
        title=title,
        description=job_description
    )
    db.add(job)
    db.flush()

    analysis = AnalysisResult(
        resume_id=resume_id,
        jd_id=job.id,
        ats_score=result["match_score"],
        status="completed"
    )
    db.add(analysis)
    db.flush()

    for name in result["matched_skills"]:
        skill = _get_or_create_skill(db, name)
        db.add(AnalysisSkill(analysis_id=analysis.id, skill_id=skill.id))

    for name in result["missing_skills"]:
        skill = _get_or_create_skill(db, name)
        db.add(MissingSkill(analysis_id=analysis.id, skill_id=skill.id))

    db.commit()
    db.refresh(analysis)

    return analysis

def save_insights(db: Session, analysis_id: uuid.UUID, insights: dict) -> None:
    """Save the AI insights for one analysis."""

    db.add(
        AIInsight(
            analysis_id=analysis_id,
            summary=insights["summary"],
            strengths=json.dumps(insights["strengths"]),
            weaknesses=json.dumps(insights["weaknesses"]),
            achievements=json.dumps(insights["achievements"]),
            recommendations=json.dumps(insights["recommendations"])
        )
    )

    db.commit()