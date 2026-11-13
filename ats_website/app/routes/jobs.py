from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models import Job, Resume, ActivityLog
from app import db
from datetime import datetime

jobs_bp = Blueprint("jobs", __name__)


@jobs_bp.route("")
@jobs_bp.route("/")
@login_required
def list_jobs():
    status_filter = request.args.get("status", "all")
    search = request.args.get("search", "").strip()
    query = Job.query.filter_by(user_id=current_user.id)
    if status_filter != "all":
        query = query.filter_by(status=status_filter)
    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))
    jobs = query.order_by(Job.created_at.desc()).all()
    return render_template("jobs/list.html", jobs=jobs, status_filter=status_filter, search=search)


@jobs_bp.route("/create", methods=["GET", "POST"])
@login_required
def create_job():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        department = request.form.get("department", "").strip()
        location = request.form.get("location", "").strip()
        job_type = request.form.get("job_type", "Full-time")
        description = request.form.get("description", "").strip()
        requirements = request.form.get("requirements", "").strip()
        required_skills = request.form.get("required_skills", "").strip()
        experience_min = request.form.get("experience_min", 0)
        experience_max = request.form.get("experience_max", 10)
        salary_min = request.form.get("salary_min") or None
        salary_max = request.form.get("salary_max") or None
        deadline_str = request.form.get("deadline", "").strip()
        status = request.form.get("status", "active")

        if not title or not description:
            flash("Job title and description are required.", "danger")
            return render_template("jobs/create.html")

        deadline = None
        if deadline_str:
            try:
                deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            except ValueError:
                pass

        job = Job(
            title=title, department=department, location=location,
            job_type=job_type, description=description, requirements=requirements,
            required_skills=required_skills,
            experience_min=int(experience_min or 0),
            experience_max=int(experience_max or 10),
            salary_min=int(salary_min) if salary_min else None,
            salary_max=int(salary_max) if salary_max else None,
            deadline=deadline, status=status, user_id=current_user.id,
        )
        db.session.add(job)
        db.session.commit()
        log = ActivityLog(user_id=current_user.id, action="Create Job",
                          details=f"Created job: {title}", ip_address=request.remote_addr)
        db.session.add(log)
        db.session.commit()
        flash(f'Job "{title}" created successfully!', "success")
        return redirect(url_for("jobs.job_detail", job_id=job.id))
    return render_template("jobs/create.html")


@jobs_bp.route("/<int:job_id>")
@login_required
def job_detail(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    resumes = Resume.query.filter_by(job_id=job_id).order_by(Resume.ats_score.desc()).all()
    status_counts = {
        "pending": sum(1 for r in resumes if r.status == "pending"),
        "reviewed": sum(1 for r in resumes if r.status == "reviewed"),
        "shortlisted": sum(1 for r in resumes if r.status == "shortlisted"),
        "rejected": sum(1 for r in resumes if r.status == "rejected"),
    }
    return render_template("jobs/detail.html", job=job, resumes=resumes, status_counts=status_counts)


@jobs_bp.route("/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    if request.method == "POST":
        job.title = request.form.get("title", job.title).strip()
        job.department = request.form.get("department", "").strip()
        job.location = request.form.get("location", "").strip()
        job.job_type = request.form.get("job_type", job.job_type)
        job.description = request.form.get("description", job.description).strip()
        job.requirements = request.form.get("requirements", "").strip()
        job.required_skills = request.form.get("required_skills", "").strip()
        job.experience_min = int(request.form.get("experience_min", 0) or 0)
        job.experience_max = int(request.form.get("experience_max", 10) or 10)
        salary_min = request.form.get("salary_min") or None
        salary_max = request.form.get("salary_max") or None
        job.salary_min = int(salary_min) if salary_min else None
        job.salary_max = int(salary_max) if salary_max else None
        job.status = request.form.get("status", job.status)
        deadline_str = request.form.get("deadline", "").strip()
        if deadline_str:
            try:
                job.deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
            except ValueError:
                pass
        job.updated_at = datetime.utcnow()
        db.session.commit()
        flash("Job updated successfully!", "success")
        return redirect(url_for("jobs.job_detail", job_id=job.id))
    return render_template("jobs/create.html", job=job)


@jobs_bp.route("/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    title = job.title
    db.session.delete(job)
    db.session.commit()
    flash(f'Job "{title}" and all associated resumes deleted.', "info")
    return redirect(url_for("jobs.list_jobs"))


@jobs_bp.route("/<int:job_id>/toggle-status", methods=["POST"])
@login_required
def toggle_status(job_id):
    job = Job.query.filter_by(id=job_id, user_id=current_user.id).first_or_404()
    job.status = "closed" if job.status == "active" else "active"
    db.session.commit()
    return jsonify({"status": job.status})
