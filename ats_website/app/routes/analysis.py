from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from app.models import Job, Resume
from app import db
import json

analysis_bp = Blueprint("analysis", __name__)


@analysis_bp.route("")
@analysis_bp.route("/")
@login_required
def index():
    jobs = Job.query.filter_by(user_id=current_user.id).order_by(Job.created_at.desc()).all()
    return render_template("analysis/index.html", jobs=jobs)


@analysis_bp.route("/compare/<int:job_id>")
@login_required
def compare(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    resumes = (
        Resume.query.filter_by(job_id=job_id)
        .order_by(Resume.ats_score.desc())
        .all()
    )
    for r in resumes:
        r.matched_list = json.loads(r.matched_skills or "[]")
        r.missing_list = json.loads(r.missing_skills or "[]")
    return render_template("analysis/compare.html", job=job, resumes=resumes)


@analysis_bp.route("/leaderboard/<int:job_id>")
@login_required
def leaderboard(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    min_score = float(request.args.get("min_score", 0))
    status_filter = request.args.get("status", "all")
    query = Resume.query.filter_by(job_id=job_id).filter(Resume.ats_score >= min_score)
    if status_filter != "all":
        query = query.filter_by(status=status_filter)
    resumes = query.order_by(Resume.ats_score.desc()).all()
    for r in resumes:
        r.matched_list = json.loads(r.matched_skills or "[]")
        r.missing_list = json.loads(r.missing_skills or "[]")
    return render_template("analysis/leaderboard.html",
                           job=job, resumes=resumes,
                           min_score=min_score, status_filter=status_filter)
