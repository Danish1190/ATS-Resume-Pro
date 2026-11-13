from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models import Job, Resume, ActivityLog
from app import db
from datetime import datetime, timedelta
from sqlalchemy import func

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    # Stats
    total_jobs = Job.query.filter_by(user_id=current_user.id).count()
    active_jobs = Job.query.filter_by(user_id=current_user.id, status="active").count()
    total_resumes = (
        db.session.query(Resume)
        .join(Job, Resume.job_id == Job.id)
        .filter(Job.user_id == current_user.id)
        .count()
    )
    shortlisted = (
        db.session.query(Resume)
        .join(Job, Resume.job_id == Job.id)
        .filter(Job.user_id == current_user.id, Resume.status == "shortlisted")
        .count()
    )

    # Average ATS score
    avg_score_result = (
        db.session.query(func.avg(Resume.ats_score))
        .join(Job, Resume.job_id == Job.id)
        .filter(Job.user_id == current_user.id, Resume.ats_score > 0)
        .scalar()
    )
    avg_score = round(avg_score_result or 0, 1)

    # Recent jobs
    recent_jobs = (
        Job.query.filter_by(user_id=current_user.id)
        .order_by(Job.created_at.desc())
        .limit(5)
        .all()
    )

    # Top resumes by ATS score
    top_resumes = (
        db.session.query(Resume)
        .join(Job, Resume.job_id == Job.id)
        .filter(Job.user_id == current_user.id, Resume.ats_score > 0)
        .order_by(Resume.ats_score.desc())
        .limit(5)
        .all()
    )

    # Score distribution
    score_ranges = {"0-25": 0, "26-50": 0, "51-75": 0, "76-100": 0}
    all_resumes = (
        db.session.query(Resume)
        .join(Job, Resume.job_id == Job.id)
        .filter(Job.user_id == current_user.id, Resume.ats_score > 0)
        .all()
    )
    for r in all_resumes:
        if r.ats_score <= 25:
            score_ranges["0-25"] += 1
        elif r.ats_score <= 50:
            score_ranges["26-50"] += 1
        elif r.ats_score <= 75:
            score_ranges["51-75"] += 1
        else:
            score_ranges["76-100"] += 1

    # Recent activity
    recent_activity = (
        ActivityLog.query.filter_by(user_id=current_user.id)
        .order_by(ActivityLog.timestamp.desc())
        .limit(8)
        .all()
    )

    # Monthly upload trend (last 6 months)
    months_data = []
    for i in range(5, -1, -1):
        month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0) - timedelta(days=30 * i)
        month_end = (month_start + timedelta(days=32)).replace(day=1)
        count = (
            db.session.query(Resume)
            .join(Job, Resume.job_id == Job.id)
            .filter(
                Job.user_id == current_user.id,
                Resume.uploaded_at >= month_start,
                Resume.uploaded_at < month_end,
            )
            .count()
        )
        months_data.append({"month": month_start.strftime("%b %Y"), "count": count})

    return render_template(
        "dashboard/index.html",
        total_jobs=total_jobs,
        active_jobs=active_jobs,
        total_resumes=total_resumes,
        shortlisted=shortlisted,
        avg_score=avg_score,
        recent_jobs=recent_jobs,
        top_resumes=top_resumes,
        score_ranges=score_ranges,
        recent_activity=recent_activity,
        months_data=months_data,
    )
